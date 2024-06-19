from typing import Optional
import uuid
from pydantic import BaseModel, Field
from sqlalchemy import (
    Boolean, Column, 
    Integer, String, DateTime, 
    UUID
    )
from sqlalchemy.sql import func
from db import Base





# Pydantic model for update payload
class VoteCreationBody ( BaseModel):
    bill_id : str = Field(example = 'some ID')
    representative_id : str = Field(example = 'some ID')
    house: str = Field(example='national' , description = 'national/senate')
    vote : str = Field(example='YES', description = 'YES/NO')
    vote_type : str = Field(example='Individual', description = 'Confidential/Concensus/Individual')
    vote_summary: Optional[str] = Field(
        example="{'Ayes':100, 'Noes':10, 'Absent':2}" ,
        description = 'A summary of how the voting happened. To use for Condidential/Concensus voting')
    

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
    vote_type = Column(String(13)) # Confidential/Concensus/Individual
    # Total counts etc --> Will help with the confidential ones
    # will be a json string of how voting panned out 
    vote_summary = Column(String(100), nullable=True)

    # In the event a representative moves houses
    # i.e was an mp then senator, using rep ID might be confusing
    house = Column(String)

    vote = Column(String) # YES/NO
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=True)
    

    def __repr__(self):
        return self.__dict__
