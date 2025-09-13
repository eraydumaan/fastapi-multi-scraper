from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from models.product import ProductCreate, ProductPublic
from db import repository as repo
from pymongo import MongoClient
import os

router = APIRouter(prefix="/products", tags=["Products"])


# -------------------------
# Health check endpoint
# -------------------------
@router.get("/health")
def health_check():
    try:
        uri = os.getenv("MONGO_URI")
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return {"status": "ok", "mongo": "connected"}
    except Exception as e:
        return {"status": "error", "mongo": str(e)}


# -------------------------
# Genel CRUD (products_col)
# -------------------------

# Yeni ürün oluşturma
@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    product_doc = product.model_dump()
    product_doc["user_id"] = ObjectId()  # test için sahte user_id

    if "source" not in product_doc:
        product_doc["source"] = "general"

    new_doc = repo.create_product_repo(product_doc)
    return ProductPublic(**new_doc)


# Tüm ürünleri listeleme
@router.get("/", response_model=list[ProductPublic])
async def list_products(limit: int = 50):
    docs = repo.list_products_repo({}, max(1, min(limit, 200)))
    return [ProductPublic(**d) for d in docs]


# -----------------------------
# Kaynağa göre özel endpointler
# -----------------------------
@router.get("/quotes")
async def list_quotes(limit: int = 50):
    return repo.list_quotes_repo(limit=max(1, min(limit, 200)))


@router.get("/books")
async def list_books(limit: int = 50):
    return repo.list_books_repo(limit=max(1, min(limit, 200)))


@router.get("/laptops")
async def list_laptops(limit: int = 50):
    return repo.list_laptops_repo(limit=max(1, min(limit, 200)))


# -----------------------------
# Tekil ürün
# -----------------------------
@router.get("/{product_id}", response_model=ProductPublic)
async def get_product(product_id: str):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    return ProductPublic(**doc)


# Ürün güncelleme
@router.put("/{product_id}", response_model=ProductPublic)
async def update_product(product_id: str, product_update: ProductCreate):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    updated_doc = repo.update_product_repo(product_id, product_update.model_dump())
    return ProductPublic(**updated_doc)


# Ürün silme
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    doc = repo.find_product_by_id_repo(product_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found.")
    repo.delete_product_repo(product_id)
    return None
