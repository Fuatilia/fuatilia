from typing import Dict, List, Optional
import uuid
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, UUID, JSON
from sqlalchemy.sql import func
from db import Base


class RoleCreationBody(BaseModel):
    permissions = Optional[List[Dict[str, str]]] = Field(
        [
            {
                "entity": "User",
                "scope": "Data",
                "permission": "Read",
                "effect": "Allow",
            },
            {
                "entity": "User",
                "scope": "List",
                "permission": "Read",
                "effect": "Allow",
            },
            {
                "entity": "User",
                "scope": "Data",
                "permission": "Update.Create",
                "effect": "Allow",
            },
            {
                "entity": "User",
                "scope": "List",
                "permission": "Update.Approve",
                "effect": "Allow",
            },
        ],
        description="Array containing dictionary with user permissions",
    )
    role = Field(String, example="Admin")

    class Config:
        from_attributes = True


class RoleUpdateBody(BaseModel):
    """
    Disallowing permission name update to prevent mistaken change of roles
    Changing a role name will mean changing the role param for all users
    """

    id: str = Field(String, example="some uuid")
    permissions = Optional[List[Dict[str, str]]] = None


class Role(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    role = Column(String, unique=True)
    permission = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=True)

    def __repr__(self):
        return self.__dict__
