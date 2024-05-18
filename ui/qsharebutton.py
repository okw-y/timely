from PySide6.QtWidgets import QPushButton, QWidget


class QShareButton(QPushButton):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
