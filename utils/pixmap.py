from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter


def colorPixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    painter = QPainter(pixmap)
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_SourceIn
    )

    painter.fillRect(pixmap.rect(), color)
    painter.end()

    return QPixmap(pixmap).scaled(
        pixmap.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
    )
