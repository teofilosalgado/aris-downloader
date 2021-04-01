from peewee import Model
from repositories import db


class BaseModel(Model):
    class Meta:
        database = db
