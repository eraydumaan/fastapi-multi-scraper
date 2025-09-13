from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from models.common import PyObjectId

class ProductCreate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[str] = None
    link: Optional[str] = None
    source: Optional[str] = "general"

class ProductPublic(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: Optional[str] = None
    text: Optional[str] = None     # quotes için
    author: Optional[str] = None   # quotes için
    price: Optional[float] = None
    stock: Optional[str] = None
    link: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[PyObjectId] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
