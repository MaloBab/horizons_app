from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    profile_picture_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    role: UserRole

    class Config:
        from_attributes = True
        

class UserShortResponse(BaseModel):
    username: str
    profile_picture_url: Optional[str] = None

    class Config:
        from_attributes = True