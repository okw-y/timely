import typing

from timely.utils.smoothscroll import QSmoothScroll
from timely.themes import QTheme

from PySide6.QtCore import QRect, Qt, Signal, QPoint
from PySide6.QtGui import (QPaintEvent, QPainter, QColor, QResizeEvent,
                           QWheelEvent, QMouseEvent, QPainterPath, QFontMetrics, QFont)
from PySide6.QtWidgets import QScrollArea, QWidget, QFrame


class QChooseData(QFrame):
    clicked = Signal(str)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._data = []
        self._rects = []

        self._height = 50
        self._margin = 5
        self._width = 60
        self._corner = 2

        self._current = -1

        self._font = QFont(self.font())
        self._font.setPointSize(8)

        self._color = QColor(QTheme.get("chooseRectColor"))
        self._label = QColor(QTheme.get("chooseLabelColor"))

    def color(self) -> QColor:
        return self._color

    def clear(self) -> None:
        self._data.clear()

    def append(self, item: int) -> None:
        self._data.append(item)

    def updateData(self, data: list[tuple[str, int]]) -> None:
        self._current = -1
        self._data = data.copy()

        self.repaint()

    def setColor(self, color: QColor) -> None:
        self._color = color

    def setCurrent(self, key: str) -> None:
        for index, (time, spent) in enumerate(self._data):
            if time == key:
                self._current = index

        self.repaint()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._data:
            return

        self._rects.clear()

        painter = QPainter(self)
        painter.setBrush(Qt.BrushStyle.SolidPattern)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()

        x, maximum = self._margin, max([value for _, value in self._data])
        for index, (key, value) in enumerate(self._data):
            height = int((value / maximum) * (self._height - 15))
            if height < self._corner * 2:
                height = self._corner * 2

            rect = QRect(
                x, self._height - height - 15, self._width, height
            )

            if index != self._current:
                path.addRoundedRect(rect, self._corner, self._corner)

            self._rects.append(
                (key, value, rect)
            )

            x += self._width + self._margin

        painter.fillPath(path, self._color)

        if self._current != -1:
            rect = QRect(self._rects[self._current][2])

            current = QPainterPath()
            current.addRoundedRect(
                rect, self._corner + 1, self._corner + 1
            )

            painter.fillPath(current, self._color.darker(200))

        labels = QPainterPath()
        x, metrics = self._margin, QFontMetrics(self._font)
        for key, _ in self._data:
            margin = (self._width // 2) - (metrics.boundingRect(key).width() // 2) - 1

            labels.addText(
                QPoint(x + margin, self._height - 2), self._font, key
            )

            x += self._width + self._margin

        painter.fillPath(labels, self._label)

        self.setFixedSize(
            ((self._width + self._margin) * len(self._data)) + self._margin, self._height
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        position = event.position().toPoint()
        for index, (key, number, rect) in enumerate(self._rects):
            if rect.contains(position):
                self._current = index

                self.clicked.emit(key)
                self.repaint()

                break


class QStatisticChooseScroller(QScrollArea):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._smooth = QSmoothScroll(self, Qt.Orientation.Horizontal)
        self._smooth.setSmoothMode(QSmoothScroll.Type.Cosine)

        self._choose = QChooseData()

        self.setWidget(self._choose)
        self.setWidgetResizable(True)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def chooseData(self) -> QChooseData:
        return self._choose

    def wheelEvent(self, event: QWheelEvent) -> None:
        event.setModifiers(
            Qt.KeyboardModifier.AltModifier
        )

        self._smooth.wheelEvent(event)


class QStatisticChooseBackground(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)


class QStatisticChoose(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._background = QStatisticChooseBackground(self)
        self._scroller = QStatisticChooseScroller(self)

    def connectData(self, trigger: typing.Callable) -> None:
        self._scroller.chooseData().clicked.connect(trigger)

    def updateData(self, data: list[tuple[str, int]]) -> None:
        self._scroller.chooseData().updateData(data)

    def updateCurrent(self, key: str) -> None:
        self._scroller.chooseData().setCurrent(key)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._background.resize(self.width(), self.height())

        self._scroller.resize(self.width() - 10, self.height() - 5)
        self._scroller.move(5, 5)
