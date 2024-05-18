import sys

from PySide6.QtGui import QResizeEvent, QFont
from PySide6.QtWidgets import QRadioButton, QFrame, QWidget, QApplication, QLabel


class QSettings(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._font = QFont(self.font())
        self._font.setBold(True)
        self._font.setPointSize(12)

        self._theme_frame = QFrame(self)

        self._theme_label = QLabel("Theme", self)
        self._theme_label.setFont(self._font)

        self._my_theme = QRadioButton("My theme", self._theme_frame)
        self._my_theme.pressed.connect(print)
        self._light_theme = QRadioButton("Light theme", self._theme_frame)
        self._dark_theme = QRadioButton("Dark theme", self._theme_frame)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._theme_frame.resize(self.width(), 200)

        self._theme_label.move(
            (self.width() // 2) - (self._theme_label.width() // 2), 10
        )

        self._my_theme.move(20, 40)
        self._light_theme.move(20, 70)
        self._dark_theme.move(20, 100)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = QSettings()
    main.show()

    sys.exit(app.exec())
