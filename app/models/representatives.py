from typing import Optional
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
    image_url : Optional[str] = Field(example = 's3//....', descrption = 'The S3 url for the image')
    gender: Optional[str] = Field( example = 'M', description ='The gender of the respensantive(M/F/OTHER)')
    representation_summary: Optional[dict] = Field('''
                                         {
                                            0:{"duration":"2017-2022", seat:"SENATOR", area_represented:"NAIROBI"},
                                            1:{"duration":"2022-NOW", seat:"GOVERNOR", area_represented:"NAIROBI"},
                                         }
                                         ''', 
                                         description = 'Indexed progression of a respresenatative , incase they change seats')
    
    class Config:
        from_attributes = True


# Pydantic model for update payload
class RepresentativeUpdateBody (BaseModel):
    id : str = Field(example = 'some uuid')
    full_name : Optional[str] = Field(example = 'Johnte')
    position : Optional[str] = Field(example='MP', description = 'MP/SENATOR/WOMEN REP/MCA' )
    position_type: Optional[str] = Field(example='ELECTED ', description = 'ELECTED/nominated')
    house : Optional[str]= Field(example="NATIONAL", description = 'NATIONAL/SENATOR')
    area_represented :Optional[str]= Field(example = "Nairobi", description="The area described under IEBC/Parliament as being represented by them")
    phone_number : Optional[str] = Field(example = '254711111111')
    image_url : Optional[str] = Field(example = 's3//....', descrption = 'The S3 url for the image')
    gender: Optional[str] = Field( example = 'M', description ='The gender of the respensantive(M/F/OTHER)')
    representation_summary: Optional[dict] = Field('''
                                         {
                                            0:{"duration":"2017-2022", seat:"SENATOR", area_represented:"NAIROBI"},
                                            1:{"duration":"2022-NOW", seat:"GOVERNOR", area_represented:"NAIROBI"},
                                         }
                                         ''', 
                                         description = 'Indexed progression of a respresentative , incase they change seats')
    
    class Config:
        from_attributes = True


class RepresenativeImageUpdate(BaseModel):
    id : str = Field(example = 'some uuid', description='uuid of the representative')
    image_type : str = Field(example = 'TWITTER_PROFILE', description = "TWITTER_PROFILE/GOK_ASSIGNED")
    image_source : str = Field(example = 'http// .. some site ..')
    source_type : Optional[str] = Field(example = 'UPLOAD', description = 'UPLOAD/WEBSITE/TWITTER/S3  , will determina how auto scarping will be done')
    base64encoded : Optional[str] = Field(example = 'someBase 64 encoded string', description = 'base64 encoding of the image' )

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
    updated_at = Column(DateTime(timezone=True), onupdate=True)
    

    def __repr__(self):
        return self.__dict__
