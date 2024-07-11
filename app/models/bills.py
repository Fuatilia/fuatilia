import enum
from typing import Optional
import uuid
from utils.enum_utils import BillStatus, Houses
from pydantic import Field, BaseModel
from sqlalchemy import (
    Boolean, Column, 
    Integer, String, DateTime, JSON,
    UUID, Enum
    )
from sqlalchemy.sql import func
from db import Base


class BillCreationBody (BaseModel):
    title: str = Field(description = 'The title of the bill e.g. Finance bill 2024')
    status: BillStatus
    brought_forth_by: str = Field(example = '6879ygv787gyv87') # rep name/ID
    supported_by: str = Field(example ='6879ygv787gyv87' ,nullable= True) # (Not sure if this happens in kenya when bringing a bill forward, but will confirm)
    house: Houses
    file_source : Optional[str] = Field(example = 'https://www.parliament...') # Add to S3 metadata
    file_data_type: Optional[str] = Field(example = 'URL', description = 'BASE64_ENCODING/URL')
    file_data : Optional[str] = Field(example = 's3//....', descrption = 'It could be a url string or base_64 encoded string depending on the datatype specifed above')
    summary: Optional[str] | None = None
    summary_created_by: Optional[str] | None = None # Id of portal user) 
    summary_upvoted_by: Optional[str] | None = None # (expert names/ids)
    summary_downvoted_by: Optional[str] | None = None # (expert names/ids)
    final_date_voted:Optional[str] | None = None # (When the bill was passed or failed) 
    topics_in_the_bill:Optional[str] | None = None # (Will help in searches)
    file_url:Optional[str] | None = None

    class Config:
        from_attributes = True
        # use_enum_values = True
    

class BillUpdateBody (BaseModel):
    id : str = Field(example = 'some uuid')
    title: Optional[str]  = None
    status: Optional[BillStatus]  = None
    brought_forth_by: Optional[str]  = None
    supported_by: Optional[str]  = None
    house: Optional[str]  = None
    file_source : Optional[str]  = None
    file_data_type: Optional[str]  = None
    file_data : Optional[str]  = None
    summary: Optional[str] = None
    summary_created_by: Optional[str] = None
    summary_upvoted_by: Optional[str] = None
    summary_downvoted_by: Optional[str] = None
    final_date_voted:Optional[str] = None
    topics_in_the_bill:Optional[str] = None
    file_url:Optional[str] = None


    class Config:
        from_attributes = True


class Bill(Base):
    __tablename__ = 'bills'

    id = Column(UUID(), primary_key=True, default = uuid.uuid4)
    title = Column(String)
    status = Column(Enum(BillStatus))
    brought_forth_by = Column(String,) # rep name/ID
    supported_by  = Column(String, nullable= True) # (Not sure if this happens in kenya when bringing a bill forward, but will confirm)
    house = Column(Enum(Houses))
    summary = Column(String, nullable= True)
    summary_created_by = Column(String, nullable= True) # Id of portal user) 
    summary_upvoted_by = Column(String, nullable= True) # (expert names/ids)
    summary_downvoted_by = Column(String, nullable= True) # (expert names/ids)
    final_date_voted = Column(String, nullable= True) # (When the bill was passed or failed) 
    topics_in_the_bill = Column(String, nullable= True) # (Will help in searches)
    file_url = Column(String, nullable= True )
    created_at = Column(DateTime, server_default= func.now())
    updated_at = Column(DateTime, onupdate= func.now())

    def __repr__(self):
        return self.__dict__
