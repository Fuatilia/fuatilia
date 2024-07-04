from enum import Enum
from typing import Dict, Optional
import uuid
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean, Column, 
    Integer, String, DateTime, JSON,
    UUID
    )
from sqlalchemy.sql import func
from db import Base



# Pydantic model for user creation Body
class RepresentativeCreationBody(BaseModel):
    full_name : str = Field(example = 'John')
    position : str = Field(example='MP', description = 'MP/SENATOR/WOMEN REP/MCA' )
    position_type: str = Field(example='ELECTED ', description = 'ELECTED/nominated')
    house : str = Field(example="NATIONAL", description = 'NATIONAL/SENATOR')
    area_represented : str= Field(example = "Nairobi", description="The area described under IEBC/Parliament as being represented by them")
    phone_number : Optional[str] = Field(example = '254711111111')
    image_source : Optional[str] = Field(example = 'https://www.parliament...') # Add to S3 metadata
    image_data_type: Optional[str] = Field(example = 'URL', description = 'BASE64_ENCODING/URL')
    image_data : Optional[str] = Field(example = 's3//....', descrption = 'It could be a url string or base_64 encoded string depending on the datatype specifed above')
    gender: Optional[str] = Field( example = 'M', description ='The gender of the respensantive(M/F/OTHER)')
    representation_summary: Optional[Dict[str, Dict[str, str]]] = Field(
                                         {
                                            "0":{"duration":"2017/01-2022/01", "seat":"SENATOR", "area_represented":"NAIROBI"},
                                            "1":{"duration":"2022/02-NOW", "seat":"GOVERNOR", "area_represented":"NAIROBI"},
                                         },
                                         nullable = True
                                         , 
                                         description = 'Indexed progression of a respresentative , incase they change seats')
    
    class Config:
        from_attributes = True


# Pydantic model for update payload
class RepresentativeUpdateBody (RepresentativeCreationBody):
    id : str = Field(example = 'some uuid')
    full_name : Optional[str] = None # Field(example = 'Johnte')
    position : Optional[str] = None # Field(example='MP', description = 'MP/SENATOR/WOMEN REP/MCA' )
    position_type: Optional[str] = None # Field(example='ELECTED ', description = 'ELECTED/nominated')
    house : Optional[str] = None # Field(example="NATIONAL", description = 'NATIONAL/SENATOR')
    area_represented :Optional[str] = None # Field(example = "Nairobi", description="The area described under IEBC/Parliament as being represented by them")
    image_url :Optional[str] = None  
    full_name: Optional[str] = None 
    position: Optional[str] = None 
    position_type: Optional[str] = None 
    house: Optional[str] = None 
    area_represented: Optional[str] = None 
    phone_number : Optional[str] = None
    image_source : Optional[str] = None
    image_data_type: Optional[str] = None
    image_data : Optional[str] = None
    gender: Optional[str] = None
    representation_summary: Optional[Dict[str, Dict[str, str]]] = None

    class Config:
        from_attributes = True


# Actual representative Model
class Representative(Base):   
    __tablename__ ='representatives' 

    id = Column(UUID(), primary_key=True, default = uuid.uuid4)
    full_name = Column(String)
    position = Column(String)
    position_type = Column(String)
    house = Column(String)
    area_represented = Column(String)
    phone_number = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    representation_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

    def __repr__(self):
        return self.__dict__



class FileType(Enum):
    PROFILE_IMAGE = 'profile_image'
    MANIFESTO = 'manifesto'
    BILL = 'bill'
    PROCEEDING = 'proceeding'
    CASE = 'case'
    ALL='all'
    VOTE='vote'