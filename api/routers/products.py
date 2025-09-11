from typing import List
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from models.product import ProductCreate, ProductPublic
from db import repository as repo
from pymongo import MongoClient
import os

router = APIRouter(prefix="/products", tags=["Products"])

# Health check endpoint (üstte olmalı)
@router.get("/health")
def health_check():
    try:
        uri = os.getenv("MONGO_URI")  # ✅ düzeltildi
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return {"status": "ok", "mongo": "connected"}
    except Exception as e:
        return {"status": "error", "mongo": str(e)}

@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    product_doc = product.model_dump()
    # Test için sahte user_id verelim
    product_doc["user_id"] = ObjectId()
    new_doc = repo.create_product_repo(product_doc)
    return ProductPublic(**new_doc)

@router.get("/", response_model=List[ProductPublic])
async def list_products(limit: int = 50):
    cursor = repo.list_products_repo({}, max(1, min(limit, 200)))
    return [ProductPublic(**p) for p in cursor]

@router.get("/{product_id}", response_model=ProductPublic)
async def get_product(product_id: str):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    return ProductPublic(**doc)

@router.put("/{product_id}", response_model=ProductPublic)
async def update_product(product_id: str, product_update: ProductCreate):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    updated_doc = repo.update_product_repo(product_id, product_update.model_dump())
    return ProductPublic(**updated_doc)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    repo.delete_product_repo(product_id)
    return None
