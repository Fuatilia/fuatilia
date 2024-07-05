from enum import Enum
from pydantic import Field
from sqlalchemy import (
    Boolean, Column, 
    Integer, String, DateTime, JSON,
    UUID, Text
    )
from sqlalchemy.sql import func
from db import Base

class BillSTatus(Enum):
    FIRST_READING = 'first_reading' 
    PASSED = 'passed' 
    FAILED = 'failed' 
    IN_PROGRESS = 'in_progress'
    ASCENTED = 'ascented'


class BillCreationBody (Base):
    title: str = Field(String, description = 'The title of the bill e.g. Finance bill 2024')
    status: BillSTatus = BillSTatus
    brought_forth_by: str = Field(String) # rep name/ID
    supported_by: str = Field(String ,nullable= True) # (Not sure if this happens in kenya when bringing a bill forward, but will confirm)
    summary:str = Field(Text, nullable= True)
    summary_created_by: str = Field(String, nullable= True) # Id of portal user) 
    summary_upvoted_by: str = Field(String, nullable= True) # (expert names/ids)
    summary_downvoted_by: str = Field(String, nullable= True) # (expert names/ids)
    final_date_voted:str = Field(String, nullable= True) # (When the bill was passed or failed) 
    topics_in_the_bill:str = Field(String, nullable= True) # (Will help in searches)
    file_url:str = Field(String, nullable= True)
    

class Bill(Base):
    id = Column(UUID) 
    title = Column(String)
    status = Column(String)
    brought_forth_by = Column(String, ) # rep name/ID
    supported_by  = Column(String, nullable= True) # (Not sure if this happens in kenya when bringing a bill forward, but will confirm)
    summary = Column(Text, nullable= True)
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
