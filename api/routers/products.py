from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from models.product import ProductCreate, ProductPublic
from models.user import UserPublic
from api.dependencies import get_current_user
from db import repository as repo
from api.dependencies import get_current_user
from pydantic import BaseModel, Field
from typing import Optional # <--- Optional'ı import etmeyi unutma
from models.common import MongoBaseModel, PyObjectId
from pymongo import MongoClient
import os 


router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, current_user: UserPublic = Depends(get_current_user)):
    product_doc = product.model_dump()
    product_doc["user_id"] = ObjectId(current_user.id)
    new_doc = repo.create_product_repo(product_doc)
    return ProductPublic(**new_doc)

@router.get("/", response_model=List[ProductPublic])
async def list_products(
    limit: int = 50,
    my_products: bool = False,
    current_user: UserPublic = Depends(get_current_user)
):
    query = {}
    if my_products:
        query["user_id"] = ObjectId(current_user.id)
    cursor = repo.list_products_repo(query, max(1, min(limit, 200)))
    return [ProductPublic(**p) for p in cursor]

@router.get("/{product_id}", response_model=ProductPublic)
async def get_product(product_id: str, current_user: UserPublic = Depends(get_current_user)):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    return ProductPublic(**doc)

@router.put("/{product_id}", response_model=ProductPublic)
async def update_product(
    product_id: str,
    product_update: ProductCreate,
    current_user: UserPublic = Depends(get_current_user)
):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    if doc["user_id"] != ObjectId(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    
    updated_doc = repo.update_product_repo(product_id, product_update.model_dump())
    return ProductPublic(**updated_doc)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, current_user: UserPublic = Depends(get_current_user)):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    if doc["user_id"] != ObjectId(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
    
    repo.delete_product_repo(product_id)
    return None

@router.get("/health")
def health_check():
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return {"status": "ok", "mongo": "connected"}
    except Exception as e:
        return {"status": "error", "mongo": str(e)}
