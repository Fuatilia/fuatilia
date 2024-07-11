from typing import Optional
import uuid
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, String, DateTime, UUID
from sqlalchemy.sql import func
from db import Base


# Pydantic model for user creation Body
class UserCreationBody(BaseModel):
    first_name: str = Field(example="Jane")
    last_name: str = Field(example="Doe")
    email: str = Field(example="user@gmail.com")
    password: str = Field(example="password1")
    user_type: str = Field(example="staff", description="expert/staff/observer")
    parent_organization: str = Field(
        example="FUATILIA", description="The organization the user belongs to"
    )
    phone_number: str = Field(example="254711111111")
    is_active: bool = Field(default=True, example=True)

    class Config:
        from_attributes = True


# Pydantic model for update payload
class UserUpdateBody(BaseModel):
    first_name: Optional[str] = Field(example="Janet")
    last_name: Optional[str] = Field(example="Doet")
    email: Optional[str] = Field(example="test@gmail.com")
    password: Optional[str] = Field(example="password2")
    user_type: Optional[str] = Field(
        example="staff", description="expert/staff/observer"
    )
    parent_organization: Optional[str] = Field(
        example="FUATILIA", description="The organization the user belongs to"
    )
    phone_number: Optional[str] = Field(example="254722222222")
    is_active: Optional[bool] = Field(example=True)

    class Config:
        from_attributes = True


# Actual user Model


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(13))
    user_type = Column(String(12))
    pass_hash = Column(String)
    parent_organization = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=True)
    is_active = Column(Boolean, default=False)

    def __repr__(self):
        return self.__dict__
