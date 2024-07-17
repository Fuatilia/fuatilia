from typing import Optional
import uuid
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, String, DateTime, UUID
from sqlalchemy.sql import func
from db import Base


"""
How permissions will work:
--------------------------

They will be like templates to use when creating roles
i.e Even if you delete a permission afterwards , if a role was created from that permisison,
    the generated dictionary in the permisisons list of a role will still remain.
    Same with updates.
    Those already created will not be affeted but those that come after will pick changes
    or if you update a role after updating a permission.
"""


class PermissionCreationBody(BaseModel):
    entity = Field(String, example="User")
    permission = Field(String, example="User.Data.Read")
    is_active = Field(Boolean, example=False, default=False)


class PermissionUpdateBody(BaseModel):
    id: str = Field(String, example="some uuid")
    entity: Optional[str] = None
    permission: Optional[str] = None
    is_active: Optional[str] = None


class Permission(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    permission = Column(String)
    entity = Column(String)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=True)
