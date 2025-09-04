from typing import Optional
from pydantic import EmailStr, BaseModel, Field
from .common import MongoBaseModel

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class UserInDB(UserBase, MongoBaseModel):
    password_hash: str

class UserPublic(UserBase, MongoBaseModel):
    pass 