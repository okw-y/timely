import typing

from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QWidget, QFrame, QPushButton


class QChooseFrame(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)


class QTypeChoose(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._choose = QChooseFrame(self)

        self._margin = 10
        self._width = 60

        self._current = 0
        self._animation = None

        self._buttons = []

    def addType(self, title: str, handler: typing.Callable = None) -> None:
        button = QPushButton(title, self)
        button.pressed.connect(self.handleButton(len(self._buttons), title, handler))

        self._buttons.append(button)

        self.updateButtons()

    def addTypes(self, types: list[str], handler: typing.Callable) -> None:
        for title in types:
            self.addType(title, handler)

    def handleButton(self, index: int, title: str, handler: typing.Callable = None) -> typing.Callable:
        def handle() -> None:
            if callable(handler):
                handler(title)

            self._animation = QPropertyAnimation(self._choose, b"pos")

            self._animation.setStartValue(self._choose.pos())
            self._animation.setEndValue(
                QPoint(self._buttons[index].x() - (self._margin // 2), self._choose.y())
            )
            self._animation.setEasingCurve(QEasingCurve.Type.InOutExpo)
            self._animation.setDuration(400)

            self._animation.start()

            self._current = index

        return handle

    def updateButtons(self) -> None:
        if not self._buttons:
            return

        x, width = self._margin, (self.width() - (self._margin * (len(self._buttons) + 1))) // len(self._buttons)
        for button in self._buttons:
            button.resize(width, self.height() - (self._margin * 2))
            button.move(x, self._margin)

            x += width + self._margin

        self._choose.resize(width + self._margin, self.height() - self._margin)
        self._choose.move(
            self._buttons[self._current].x() - (self._margin // 2), self._margin // 2
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.updateButtons()
