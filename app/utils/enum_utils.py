from enum import Enum
from django.db import models


class FileType(Enum):
    IMAGE = "IMAGE"
    MANIFESTO = "MANIFESTO"
    BILL = "BILL"
    PROCEEDING = "PROCEEDING"
    CASE = "CASE"
    ALL = "ALL"
    VOTE = "VOTE"


class FileTypeTextChoices(models.TextChoices):
    IMAGE = "IMAGE"
    MANIFESTO = "MANIFESTO"
    BILL = "BILL"
    PROCEEDING = "PROCEEDING"
    CASE = "CASE"
    ALL = "ALL"
    VOTE = "VOTE"
