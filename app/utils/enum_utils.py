from enum import Enum
from django.db import models


class FileTypeEnum(Enum):
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


class HouseChoices(models.TextChoices):
    NATIONAL = "NATIONAL"
    SENATE = "SENATE"
    ALL = "ALL"  # If it's the same bill in all houses


class VoteTypeChoicesChoices(models.TextChoices):
    CONFIDENTIAL = "CONFIDENTIAL"
    CONCENSUS = "CONCENSUS"
    INDIVIDUAL = "INDIVIDUAL"
