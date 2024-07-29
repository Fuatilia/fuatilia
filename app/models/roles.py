from typing import Dict, List, Optional
import uuid
from db import Base
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, UUID, JSON
from sqlalchemy.sql import func


class RoleCreationBody(BaseModel):
    permissions: Optional[List[str]] = Field(
        [
            "c39064d7-73de-4c76-97a4-fd0818e32dee",
            "d036effc-cc7d-4291-8fa4-1159fa1ac1a1",
        ],
        description="Array containing ids of permissions",
    )
    role: str = Field(String, example="Admin")

    class Config:
        from_attributes = True


class RoleUpdateBody(BaseModel):
    """
    Disallowing permission name update to prevent mistaken change of roles
    Changing a role name will mean changing the role param for all users
    """

    id: str = Field(String, example="some uuid")
    permissions: Optional[List[Dict[str, str]]] = None


class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    role = Column(String, unique=True)
    permissions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=True)

    def __repr__(self):
        return self.__dict__
