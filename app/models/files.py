from typing import Dict
from pydantic import BaseModel, Field


class FileUploadBody(BaseModel):
    file_name: str = Field(example="user image.jpeg")
    metadata: Dict[str, str] | None = Field(
        example={"creation_date": "2017/01-2022/01", "uploaded_from": "gok"}
    )
    base64encoding: str = Field(
        example="/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAUDB ...",
        description="Base64 encoding of the file",
    )

    class Config:
        from_attributes = True
