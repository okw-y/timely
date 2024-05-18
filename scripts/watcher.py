import time
import datetime

import win32api
import win32gui
import win32process

from pathlib import Path
from peewee import CharField, TimestampField, IntegerField, Model, SqliteDatabase


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


session = SqliteDatabase(f"{Path.cwd()}\\files\\db\\spent-time.db")


class SpentTime(Model):
    path = CharField()
    timestamp = TimestampField()
    spent = IntegerField()

    class Meta:
        database = session


SpentTime.create_table()

while True:
    try:
        title, path = getCurrentApplication()
        if SpentTime.select().where((SpentTime.path == path) & (SpentTime.timestamp == datetime.date.today())).exists():
            application = SpentTime.select().where(
                (SpentTime.path == path) & (SpentTime.timestamp == datetime.date.today())
            ).get()

            application.spent += 1
            application.save()
        else:
            SpentTime(
                path=path, timestamp=datetime.date.today(), spent=1
            ).save()
    except Exception as error:
        print(error)

    time.sleep(1)
