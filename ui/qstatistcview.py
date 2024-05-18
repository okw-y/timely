import typing
from pathlib import Path

from timely.utils import application, pixmap
from timely.themes import QTheme

from PySide6.QtCharts import QPieSlice, QChart, QChartView, QPieSeries, QLegend
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QResizeEvent, QColor, QBrush, QPainter, QFont, QPaintEvent, QPainterPath, QFontMetrics, \
    QPixmap
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QSizePolicy


class QStatisticLegend(QFrame):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._margin = 10
        self._corner = 5

        self._font = QFont(self.font())
        self._font.setBold(True)

        self._color = QColor(QTheme.get("statisticAppBackground"))

        self._data = []

    def setData(self, data: list[tuple[str, QColor, float, float]]) -> None:
        self._data = data.copy()

        self.repaint()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self._data:
            return

        painter = QPainter(self)
        painter.setBrush(Qt.BrushStyle.SolidPattern)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        metrics = QFontMetrics(self._font)

        y, height = self._margin, (self.height() - ((len(self._data) + 1) * self._margin)) // len(self._data)
        for title, color, spent, percent in self._data:
            title = metrics.elidedText(
                title, Qt.TextElideMode.ElideRight, self.width() - (self._margin * 4)
            )

            time = application.convertSpentTime(spent)
            percentage = f"{percent}%"

            path = QPainterPath()
            path.addRoundedRect(
                QRect(self._margin // 2, y, self.width() - self._margin, height), self._corner, self._corner
            )

            start = ((self.width() - (self._margin * 2)) // 2)

            title_margin = start - (metrics.boundingRect(title).width() // 2)
            spent_margin = (start // 2) - (metrics.boundingRect(time).width() // 2)
            percent_margin = (start // 2) - (metrics.boundingRect(percentage).width() // 2)

            labels = QPainterPath()
            labels.addText(
                QPoint(self._margin + title_margin, y + (self._margin * 2)), self._font, title
            )
            labels.addText(
                QPoint(self._margin + spent_margin, int(y + (self._margin * 3.5))), self._font, time
            )
            labels.addText(
                QPoint(start + self._margin + percent_margin, int(y + (self._margin * 3.5))), self._font, percentage
            )

            painter.fillPath(path, self._color)
            painter.fillPath(labels, color)

            y += height + self._margin


class QIconedStatistic(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._font = QFont(self.font())
        self._font.setPointSize(10)
        self._font.setBold(True)

        self._time_icon = QLabel(self)
        self._time_icon.setScaledContents(True)
        self._time_icon.resize(20, 20)
        self._time_icon.move(15, 15)

        self._calendar_icon = QLabel(self)
        self._calendar_icon.setScaledContents(True)
        self._calendar_icon.resize(20, 20)
        self._calendar_icon.move(148, 15)

        self._time_text = QLabel(self)
        self._time_text.setFont(self._font)
        self._time_text.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._time_text.resize(68, 30)
        self._time_text.move(35, 10)

        self._calendar_text = QLabel(self)
        self._calendar_text.setFont(self._font)
        self._calendar_text.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._calendar_text.resize(68, 30)
        self._calendar_text.move(168, 10)

        QTheme.changed.append(self.iconChanged)

        self.iconChanged()

    def iconChanged(self) -> None:
        self._time_icon.setPixmap(
            pixmap.colorPixmap(
                QPixmap(f"{Path.cwd()}/files/icons/time.png"), QColor(QTheme.get("iconColor"))
            )
        )

        self._calendar_icon.setPixmap(
            pixmap.colorPixmap(
                QPixmap(f"{Path.cwd()}/files/icons/calendar.png"), QColor(QTheme.get("iconColor"))
            )
        )

    def updateStatistic(self, total: int, time: str) -> None:
        self._time_text.setText(application.convertSpentTime(total))
        self._calendar_text.setText(time.replace("_", "All"))

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setBrush(Qt.BrushStyle.SolidPattern)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QRect(9, 10, 118, 30), 5, 5)
        path.addRoundedRect(QRect(138, 10, 118, 30), 5, 5)

        painter.fillPath(path, QColor(QTheme.get("statisticAppBackground")))


class QStatisticView(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self._font = QFont(self.font())
        self._font.setPointSize(14)
        self._font.setBold(True)

        self._chart = QChart()
        self._chart.createDefaultAxes()
        self._chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self._chart.setBackgroundBrush(
            QBrush(QColor(QTheme.get("statisticAppBackground")))
        )

        self._chart.legend().setBorderColor(
            QColor(QTheme.get("statisticAppBackground"))
        )
        self._chart.legend().setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        self._chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        self._chart.legend().hide()

        self._series = QPieSeries(self._chart)
        self._series.setPieSize(0.7)
        self._series.setHoleSize(0.35)

        self._chart.addSeries(self._series)

        self._view = QChartView(self)
        self._view.setChart(self._chart)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setBackgroundBrush(
            QBrush(QColor(QTheme.get("statisticViewBackground")))
        )

        self._iconed_statistic = QIconedStatistic(self)

        self._all_time = QLabel(self)
        self._all_time.setFont(self._font)
        self._all_time.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._all_time.hide()

        self._legend = QStatisticLegend(self)

    def updateLegend(self) -> None:
        data = []
        for slices in self._series.slices():
            data.append(
                (slices.label(), slices.color(), slices.value(), round(slices.percentage() * 100, 1))
            )

        self._legend.setData(
            sorted(data, reverse=True, key=lambda value: value[2])
        )

    def setData(self, time: str, data: list[tuple[str, int]]) -> None:
        self._series.clear()

        for path, spent in sorted(data, reverse=True, key=lambda value: value[1])[:5]:
            name = application.getApplicationTitle(path)

            slices = self._series.append(name, spent)
            slices.setBorderColor(
                QColor(QTheme.get("statisticAppBackground"))
            )

            slices.hovered.connect(self.sliceHoveredEvent(slices))
            slices.colorChanged.connect(self.updateLegend)

            slices.setColor(QTheme.pie())

        self._all_time.setText(
            f"Total time: {application.convertSpentTime(sum([spent for _, spent in data]))}"
        )

        self._iconed_statistic.updateStatistic(
            sum([spent for _, spent in data]), time
        )

    def sliceHoveredEvent(self, slices: QPieSlice) -> typing.Callable:
        if self._chart.animationOptions() == QChart.AnimationOption.NoAnimation:
            self._chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)

        slices.setExplodeDistanceFactor(0.05)

        def eventReader(state: bool) -> None:
            slices.setExploded(state)

        return eventReader

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._view.resize(int(self.width() // 1.5), self.height() - 40)
        self._view.move(0, 40)

        self._iconed_statistic.resize(self._view.width(), 40)

        self._all_time.resize(self._view.width(), 40)
        self._all_time.move(10, 10)

        self._legend.resize(self.width() // 3, self.height())
        self._legend.move(self._view.width(), 0)
