import os
from peewee import SqliteDatabase

path: str = os.path.join("output", "db.db")
db: SqliteDatabase = SqliteDatabase(path)
