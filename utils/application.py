import os

import win32api
import win32gui
import win32process


def getApplicationPath(hwnd: int) -> str:
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process = win32api.OpenProcess(0x0400, False, pid)

    try:
        location = win32process.GetModuleFileNameEx(process, 0)
    finally:
        win32api.CloseHandle(process)

    return location or ""


def getCurrentApplication() -> tuple[str, str]:
    hwnd = win32gui.GetForegroundWindow()

    return win32gui.GetWindowText(hwnd), getApplicationPath(hwnd)


def getFileProperties(path: str) -> dict[str, dict | object]:
    names = ("Comments", "InternalName", "ProductName",
             "CompanyName", "LegalCopyright", "ProductVersion",
             "FileDescription", "LegalTrademarks", "PrivateBuild",
             "FileVersion", "OriginalFilename", "SpecialBuild")

    properties = {
        "FixedFileInfo": None,
        "StringFileInfo": None,
        "FileVersion": None
    }

    try:
        info = win32api.GetFileVersionInfo(path, "\\")

        properties["FixedFileInfo"] = info
        properties["FileVersion"] = (f"{info['FileVersionMS'] / 65536}."
                                     f"{info['FileVersionMS'] % 65536}."
                                     f"{info['FileVersionLS'] / 65536}."
                                     f"{info['FileVersionLS'] % 65536}")

        language, codepage = win32api.GetFileVersionInfo(path, "\\VarFileInfo\\Translation")[0]

        string_info = {}
        for name in names:
            string_info[name] = win32api.GetFileVersionInfo(
                path, u"\\StringFileInfo\\%04X%04X\\%s" % (language, codepage, name)
            )

        properties["StringFileInfo"] = string_info
    except Exception as _:
        del _

    return properties


def getApplicationTitle(path: str) -> str:
    properties, name = getFileProperties(path), os.path.basename(path).replace(".exe", "").capitalize()
    if properties["StringFileInfo"]:
        name = properties["StringFileInfo"]["FileDescription"] or name

    return name


def convertSpentTime(spent: int) -> str:
    time = f"{int(spent)}s"
    if spent > 3659:
        time = f"{round(spent / 3600, 2)}h"
    elif spent > 59:
        time = f"{round(spent / 60, 2)}m"

    return time
