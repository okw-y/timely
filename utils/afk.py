from ctypes import Structure, windll, c_uint, sizeof, byref


class LASTINPUTINFO(Structure):
    _fields_ = [
        ("cbSize", c_uint),
        ("dwTime", c_uint),
    ]


def getIdleDuration() -> float:
    info = LASTINPUTINFO()
    info.cbSize = sizeof(info)

    windll.user32.GetLastInputInfo(byref(info))

    return (windll.kernel32.GetTickCount() - info.dwTime) / 1000
