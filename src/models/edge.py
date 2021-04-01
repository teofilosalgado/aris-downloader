from peewee import AutoField, ForeignKeyField

from .base import BaseModel
from .node import Node


class Edge(BaseModel):
    id = AutoField()
    source = ForeignKeyField(Node)
    destination = ForeignKeyField(Node)
