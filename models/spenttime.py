from pathlib import Path
from peewee import CharField, TimestampField, IntegerField, Model, SqliteDatabase


session = SqliteDatabase(f"{Path.cwd()}\\files\\db\\spent-time.db")  # f"{Path.cwd()}\\files\\db\\spent-time.db"


class SpentTime(Model):
    path = CharField()
    timestamp = TimestampField()
    spent = IntegerField()

    class Meta:
        database = session
