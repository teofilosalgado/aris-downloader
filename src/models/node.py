from peewee import AutoField, BooleanField, TextField

from .base import BaseModel


class Node(BaseModel):
    id = AutoField()
    url = TextField(unique=True)
    title = TextField()
    is_model = BooleanField()
    database_name = TextField()
    is_png_downloaded = BooleanField()
    is_pdf_downloaded = BooleanField()
