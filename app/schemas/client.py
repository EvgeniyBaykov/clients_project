from enum import Enum
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


class ClientCreate(BaseModel):
    avatar_url: str = None
    gender: GenderEnum
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class Client(BaseModel):
    id: int
    avatar: str = None
    gender: GenderEnum
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class AvatarUpload(BaseModel):
    avatar: UploadFile
