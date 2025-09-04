# models/product.py

from pydantic import BaseModel, Field
from typing import Optional # <--- Optional'ı import ediyoruz
from .common import MongoBaseModel, PyObjectId

class ProductBase(BaseModel):
    title: str
    
    # DÜZELTME 1: Bu alanları opsiyonel yapıyoruz.
    # Artık bir ürünün fiyatı veya stok durumu olmak zorunda değil.
    price: Optional[float] = None
    stock: Optional[str] = None
    
    link: str
    
    # DÜZELTME 2: Verinin kaynağını tutacak yeni alanı ekliyoruz.
    source: str

class ProductCreate(ProductBase):
    pass

class ProductPublic(ProductBase, MongoBaseModel):
    user_id: PyObjectId = Field(...)