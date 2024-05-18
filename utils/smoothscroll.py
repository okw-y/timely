import collections
import math

from PySide6.QtCore import Qt, QDateTime, QPoint, QTimer
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QAbstractScrollArea, QApplication


class QSmoothScroll:
    class Type:
        NoSmooth = 0
        Constant = 1
        Linear = 2
        Quadrati = 3
        Cosine = 4

    def __init__(self, target: QAbstractScrollArea, orient: Qt.Orientation = Qt.Orientation.Vertical) -> None:
        self._target = target
        self._orient = orient

        self._smooth_mode = 0

        self._fps = 60
        self._duration = 250

        self._steps = 0
        self._ratio = 1.5
        self._acceleration = 1

        self._last_event = None
        self._last_pos = None
        self._last_global_pos = None

        self._scroll_stamps = collections.deque()
        self._steps_left_queue = collections.deque()

        self._timer = QTimer(self._target)
        self._timer.timeout.connect(self.smoothMode)

    def setSmoothMode(self, mode: int) -> None:
        self._smooth_mode = mode

    def smoothMode(self) -> None:
        delta = 0

        for chunk in self._steps_left_queue:
            delta += self.subDelta(chunk[0], chunk[1])

            chunk[1] -= 1

        while self._steps_left_queue and not self._steps_left_queue[0][1]:
            self._steps_left_queue.popleft()

        if self._orient == Qt.Orientation.Vertical:
            pixel = QPoint(round(delta), 0)
            bar = self._target.verticalScrollBar()
        else:
            pixel = QPoint(0, round(delta))
            bar = self._target.horizontalScrollBar()

        event = QWheelEvent(
            self._last_pos,
            self._last_global_pos,
            pixel,
            QPoint(round(delta), 0),
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollBegin,
            False
        )

        QApplication.sendEvent(bar, event)

        if not self._steps_left_queue:
            self._timer.stop()

    def subDelta(self, delta: int, left: int) -> int:
        maximum = self._steps / 2
        absolute = abs(self._steps - left - maximum)

        # print(delta, left)

        resource = 0
        if self._smooth_mode == 0:
            resource = 0
        if self._smooth_mode == 1:
            resource = (delta / abs(delta)) * (2 * maximum / self._steps) * 10
        if self._smooth_mode == 2:
            resource = (delta / abs(delta)) * (2 * maximum / self._steps * (maximum - absolute) / maximum) * 10
        if self._smooth_mode == 3:
            resource = 3 / 4 / maximum * (1 - absolute * absolute / maximum / maximum) * delta
        if self._smooth_mode == 4:
            resource = (math.cos(absolute * math.pi / maximum) + 1) / (2 * maximum) * delta

        return resource

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y() if event.angleDelta().y() else event.angleDelta().x()
        if self._smooth_mode == 0 or abs(delta) % 120 != 0:
            return QAbstractScrollArea.wheelEvent(self._target, event)

        self._scroll_stamps.append(
            now := QDateTime.currentDateTime().toMSecsSinceEpoch()
        )
        while now - self._scroll_stamps[0] > 500:
            self._scroll_stamps.popleft()

        acceleration = min(len(self._scroll_stamps) / 15, 1)

        self._last_pos = event.position()
        self._last_global_pos = event.globalPosition()

        self._steps = self._fps * self._duration / 1000

        delta *= self._ratio
        if self._acceleration > 0:
            delta += delta * self._acceleration * acceleration

        self._steps_left_queue.append([delta, self._steps])
        self._timer.start(int(1000 / self._fps))
