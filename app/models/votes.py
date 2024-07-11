from typing import Dict, Optional
import uuid
from utils.enum_utils import Houses, VoteType
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean, Column, 
    Integer, String, DateTime, 
    UUID, Enum, JSON
    )
from sqlalchemy.sql import func
from db import Base


# Pydantic model for update payload
class VoteCreationBody ( BaseModel):
    bill_id : str = Field(example = 'some ID')
    representative_id : str = Field(example = 'some ID')
    house: Houses
    vote : str = Field(example='YES', description = 'YES/NO/ABSENT  ...etc')
    vote_type : VoteType
    vote_summary:Optional[Dict[str, str|int]] = Field(
        example= {'Ayes':100, 'Noes':10, 'Absent':2} ,
        description = 'A summary of how the voting happened. To use for Condidential/Concensus voting')
    
    class Config:
        from_attributes = True


# Pydantic model for update payload
class VoteUpdateBody ( BaseModel):
    id: str = Field(example= 'some ID')
    bill_id: Optional[str] = None
    representative_id : Optional[str] = None
    house: Optional[Houses] = None
    vote: Optional[str] = None
    vote_type: Optional[VoteType] = None
    vote_summary: Optional[Dict[str, str|int]] = None

    class Config:
        from_attributes = True


# Actual user Model
class Vote(Base):   
    __tablename__ ='votes' 

    id = Column(UUID(), primary_key=True, default = uuid.uuid4)
    # Probably have bill ID as a foreign key for fetching etc.
    bill_id = Column(String(50))
    # Probably have represantative ID as a foreign key for fetching etc.
    representative_id = Column(String(50))
    vote_type = Column(Enum(VoteType)) # Confidential/Concensus/Individual
    # Total counts etc --> Will help with the confidential ones
    # will be a json string of how voting panned out 
    vote_summary = Column(JSON(100), nullable=True)

    # In the event a representative moves houses
    # i.e was an mp then senator, using rep ID might be confusing
    house = Column(Enum(Houses))
    vote = Column(String) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=True)
    

    def __repr__(self):
        return self.__dict__
