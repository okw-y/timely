import datetime
import os
import sys

from timely.utils import (titlebar, timestamp,
                          pixmap, application,
                          afk, sound)
from timely.models import SpentTime
from timely.themes import QTheme
from timely.ui import (QStatisticView, QStatisticChoose,
                       QApplicationList, QTypeChoose,
                       QShareButton)

from PySide6.QtCore import QTimer, QFileSystemWatcher, Qt
from PySide6.QtGui import (QImage, QClipboard, QPixmap,
                           QColor, QResizeEvent)
from PySide6.QtWidgets import QWidget, QApplication, QMenu, QSystemTrayIcon


class QWatcher(QWidget):
    def __init__(self) -> None:
        super().__init__()

        SpentTime.create_table()

        self._statistic = None
        self._path = os.path.dirname(os.path.realpath(__file__))

        self._timer = QTimer()
        self._timer.timeout.connect(self.watch)  # noqa

        self._menu = QMenu()

        self._menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._menu.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self._menu.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint)

        self._menu.addAction("Statistic", self.statistic)
        self._menu.addAction("Quit", sys.exit)

        self._tray = QSystemTrayIcon(self)
        self._tray.setContextMenu(self._menu)
        self._tray.setToolTip("Timely [BETA+++]")
        self._tray.setIcon(
            QPixmap(f"{self._path}/files/icons/timely-icon.png")
        )
        self._tray.show()

        self._watcher = QFileSystemWatcher([f"{self._path}/files/themes/my.theme"])
        self._watcher.fileChanged.connect(self.updateTheme)  # noqa

        app.setStyleSheet(
            QTheme.load(f"{self._path}/files/themes/my.theme")
        )

    @staticmethod
    def watch() -> None:
        try:
            if afk.getIdleDuration() > 300 and not sound.mediaIsPlaying():
                return

            title, path = application.getCurrentApplication()
            if SpentTime.select().where(
                    (SpentTime.path == path) & (SpentTime.timestamp == datetime.date.today())).exists():
                spent_time = SpentTime.select().where(
                    (SpentTime.path == path) & (SpentTime.timestamp == datetime.date.today())
                ).get()

                spent_time.spent += 1
                spent_time.save()
            else:
                SpentTime(
                    path=path, timestamp=datetime.date.today(), spent=1
                ).save()
        except Exception as _:
            del _

    def updateTheme(self) -> None:
        app.setStyleSheet(
            QTheme.load(f"{self._path}/files/themes/my.theme")
        )

        if self._statistic:
            self._statistic.updateApplicationProperty()

    def statistic(self) -> None:
        self._statistic = QMain()
        self._statistic.show()

    def start(self) -> None:
        self._timer.start(1000)


class QMain(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setFixedSize(400, 700)

        self._path = os.path.dirname(os.path.realpath(__file__))
        self._applications = []

        self._types_choose = QTypeChoose(self)
        self._types_choose.addTypes(
            ["All", "Year", "Month", "Day"], self.chooseDeltaType
        )

        self._statistic_choose = QStatisticChoose(self)
        self._statistic_choose.connectData(self.chooseDelta)

        self._statistic_view = QStatisticView(self)
        self._application_list = QApplicationList(self)

        self._share_button = QShareButton(self)
        self._share_button.pressed.connect(self.saveStatisticToClipboard)

        self.updateApplicationProperty()

    def updateApplicationProperty(self) -> None:
        self.chooseDeltaType("all")

        self.setWindowTitle(f"Timely ({os.environ['COMPUTERNAME']}/{os.environ['USERNAME']})")
        self.setWindowIcon(
            pixmap.colorPixmap(QPixmap(f"{self._path}/files/icons/icon.png"), QColor(QTheme.get("titleBarIconColor")))
        )

        if QTheme.get("titleBarTheme") == "dark":
            titlebar.setTileBarDarkTheme(self.window().winId())

        self._share_button.setIcon(
            pixmap.colorPixmap(QPixmap(f"{self._path}/files/icons/share.png"), QColor(QTheme.get("iconColor")))
        )

    def saveStatisticToClipboard(self) -> None:
        image = QImage(
            self._statistic_view.width() * 5,
            self._statistic_view.height() * 5,
            QImage.Format.Format_ARGB32
        )
        image.setDevicePixelRatio(5)

        self._statistic_view.render(image)

        QApplication.clipboard().setImage(
            image, QClipboard.Mode.Clipboard
        )

    def chooseDeltaType(self, type: str) -> None:
        deltas, applications = timestamp.selectByDeltaType(type.lower(), SpentTime)

        self._applications = applications.copy()

        self._statistic_choose.updateData([])
        if type.lower() != "all":
            self._statistic_choose.updateData(deltas)

        self.chooseDelta(deltas[0][0])
        self._statistic_choose.updateCurrent(
            deltas[0][0]
        )

    def chooseDelta(self, time: str) -> None:
        data = {}
        for path, spent in self._applications[time]:  # noqa
            if path not in data:
                data[path] = 0

            data[path] += spent

        self._statistic_view.setData(time, list(data.items()))
        self._application_list.setData(list(data.items()))

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._types_choose.resize(self.width() - 40, 40)
        self._types_choose.move(0, 0)

        self._share_button.resize(40, 40)
        self._share_button.move(self.width() - 41, 0)

        self._statistic_choose.resize(self.width() - 14, 60)
        self._statistic_choose.move(7, 40)

        self._statistic_view.resize(self.width(), 300)
        self._statistic_view.move(0, 100)

        self._application_list.resize(self.width() - 10, 300)
        self._application_list.move(0, 400)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    main = QWatcher()
    main.start()

    sys.exit(app.exec())
