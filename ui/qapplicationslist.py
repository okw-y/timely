from timely.themes import QTheme
from timely.utils import application
from timely.utils.smoothscroll import QSmoothScroll

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPaintEvent, QPainter, QPainterPath, QFont, QColor, QWheelEvent, QFontMetrics
from PySide6.QtWidgets import QFrame, QWidget, QScrollArea


class QApplicationListFrame(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._margin = 10
        self._height = 50
        self._corner = 5

        self._font = QFont(self.font())
        self._font.setPointSize(13)
        self._font.setBold(True)

        self._metrics = QFontMetrics(self._font)

        self._data = []

    def setData(self, data: list[tuple[str, str]]) -> None:
        self._data = data.copy()

        self.repaint()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._data:
            return

        painter = QPainter(self)
        painter.setBrush(Qt.BrushStyle.SolidPattern)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        spent = QPainterPath()
        text = QPainterPath()

        y, width = 0, self.width()
        for title, time in self._data:
            title = self._metrics.elidedText(
                title, Qt.TextElideMode.ElideRight, int(width // 1.5) - (self._margin * 4)
            )

            path.addRoundedRect(
                QRect(self._margin, y, width - (self._margin * 2), self._height), self._corner, self._corner
            )
            spent.addRoundedRect(
                QRect(
                    int(width // 1.5) - (self._margin // 2),
                    y + (self._margin // 2),
                    (width // 3) - self._margin,
                    self._height - self._margin
                ), self._corner - 1, self._corner - 1
            )

            text.addText(
                QPoint(self._margin * 2, y + 32), self._font, title
            )
            text.addText(
                QPoint(int(width // 1.5) + self._margin, y + 32), self._font, time
            )

            y += self._height + self._margin

        painter.fillPath(path, QColor(QTheme.get("applicationListItem")))
        painter.fillPath(spent, QColor(QTheme.get("applicationListSpent")))
        painter.fillPath(text, QColor(QTheme.get("applicationListLabel")))

        self.setFixedSize(width, y)


class QApplicationList(QScrollArea):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._smooth = QSmoothScroll(self, orient=Qt.Orientation.Vertical)
        self._smooth.setSmoothMode(QSmoothScroll.Type.Cosine)

        self._widget = QApplicationListFrame()

        self.setWidget(self._widget)
        self.setWidgetResizable(True)

        # self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def setData(self, data: list[tuple[str, int]]) -> None:
        data = sorted(data, reverse=True, key=lambda item: item[1])

        self._widget.setData(
            [(application.getApplicationTitle(path), application.convertSpentTime(spent)) for path, spent in data]
        )

    def wheelEvent(self, event: QWheelEvent) -> None:
        self._smooth.wheelEvent(event)
