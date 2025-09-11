from pydantic import BaseModel, Field
from typing import Optional
from .common import MongoBaseModel, PyObjectId

class ProductBase(BaseModel):
    id: str = Field(alias="_id")
    title: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[str] = None
    link: Optional[str] = None
    source: Optional[str] = None
    user_id: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductPublic(ProductBase, MongoBaseModel):
    id: str = Field(alias="_id")
    user_id: Optional[str] = None
