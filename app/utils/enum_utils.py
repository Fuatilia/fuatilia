from enum import Enum

class FileType(Enum):
    PROFILE_IMAGE = 'profile_image'
    MANIFESTO = 'manifesto'
    BILL = 'bill'
    PROCEEDING = 'proceeding'
    CASE = 'case'
    ALL='all'
    VOTE='vote'