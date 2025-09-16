from pydantic import BaseModel, EmailStr, Field, ConfigDict
from bson import ObjectId
from models.common import PyObjectId


class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: str = "user"  # "user" | "admin"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserDB(UserBase):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    hashed_password: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class UserPublic(UserBase):
    id: str = Field(..., alias="_id")  # dışarıya string olarak dönsün

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
