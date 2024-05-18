from timely.utils import theme


class QTheme(object):
    _last = 1
    _data = {}

    changed = []

    @classmethod
    def pie(cls) -> str:
        if cls._last == 5:
            cls._last = 0
        cls._last += 1

        return cls.get(f"pieGraphColor{cls._last}")

    @classmethod
    def get(cls, key: str) -> str:
        return cls._data.get(key, "")

    @classmethod
    def load(cls, path: str) -> str:
        cls._data = theme.parse(path)

        for function in cls.changed:
            function()

        return f"QMain, QStatisticView {{ background: {cls.get('background')}; }} " \
               f"QLabel {{ color: {cls.get('labelColor')}; }} " \
               f"QChooseData {{ background: {cls.get('chooseData')}; }} " \
               f"QStatisticChooseBackground {{ background: {cls.get('statisticChoose')}; border-radius: 5px; }} " \
               f"QApplicationListFrame {{ background: {cls.get('applicationList')}; }} " \
               f"QScrollArea {{ border: none; background: transparent; }} " \
               f"QScrollBar:vertical {{ background-color: {cls.get('scrollbarBackground')}; width: 6px; " \
               f"margin: 1px 0px 11px 0px; border-radius: 3px; " \
               f"border: 1px transparent {cls.get('scrollbarBackground')}; }} " \
               f"QScrollBar::handle:vertical {{ background-color: {cls.get('scrollbarHandleColor')}; " \
               f"min-height: 6px; border-radius: 3px; }} " \
               f"QScrollBar::sub-line:vertical {{ background-color: transparent; color: transparent; }} " \
               f"QScrollBar::add-line:vertical {{ background-color: transparent; color: transparent; }} " \
               f"QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{ background: none; }} " \
               f"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }} " \
               f"QPushButton {{ background: transparent; color: {cls.get('labelColor')}; font-weight: bold; }}" \
               f"QShareButton {{ background: {cls.get('shareButtonColor')}; color: {cls.get('labelColor')}; " \
               f"font-weight: bold; border: none; border-radius: 5px; margin: 5px; }}" \
               f"QShareButton:hover {{ background: {cls.get('shareButtonHoverColor')}; }}" \
               f"QChooseFrame {{ background: {cls.get('chooseDeltaTypeColor')}; border-radius: 6px; margin: 1px; }}" \
               f"QMenu {{ background: {cls.get('contextMenuBackground')}; color: {cls.get('contextMenuItemColor')}; " \
               f"border-radius: 5px; font-size: 10pt; padding: 3px; }} " \
               f"QMenu::item {{ background: transparent; border: none; padding: 3px 15px 3px 15px; }} " \
               f"QMenu::item:selected {{ background-color: {cls.get('contextMenuSelectedBackground')}; " \
               f"border-radius: 3px; }} QMenu::icon {{ padding-left: 5px; }}"
