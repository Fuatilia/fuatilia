from enum import Enum


class FileType(Enum):
    PROFILE_IMAGE = "profile_image"
    MANIFESTO = "manifesto"
    BILL = "bill"
    PROCEEDING = "proceeding"
    CASE = "case"
    ALL = "all"
    VOTE = "vote"


class BillStatus(Enum):
    FIRST_READING = "first_reading"
    PASSED = "passed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    ASCENTED = "ascented"


class Houses(Enum):
    NATIONAL = "national"
    SENATE = "senate"


class VoteType(Enum):
    CONFIDENTIAL = "confidential"
    CONCENSUS = "concensus"
    INDIVIDUAL = "individual"
