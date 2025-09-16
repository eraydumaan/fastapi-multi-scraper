from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from models.product import ProductCreate, ProductPublic
from db import repository as repo
from pymongo import MongoClient
import os
from models.user import UserPublic
from api.dependencies import get_current_user, require_role
from core.settings import get_settings

settings = get_settings()
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

router = APIRouter(prefix="/products", tags=["Products"])

# -------------------------
# Stats endpoint
# -------------------------
@router.get("/stats")
def product_stats(user=Depends(get_current_user)):
    pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    stats = list(db.products.aggregate(pipeline))
    return {"stats": stats}


# -------------------------
# User specific endpoints
# -------------------------
@router.get("/mine")
def list_my_products(user: UserPublic = Depends(get_current_user)):
    return {"message": f"{user.username} ürünleri"}


@router.get("/admin")
def list_all_products(admin: UserPublic = Depends(require_role("admin"))):
    return {"message": "Admin tüm ürünleri görebilir"}


# -------------------------
# Health check
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
# CRUD operations
# -------------------------
@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    product_doc = product.model_dump()
    product_doc["user_id"] = ObjectId()
    if "source" not in product_doc:
        product_doc["source"] = "general"
    new_doc = repo.create_product_repo(product_doc)
    return ProductPublic(**new_doc)


@router.get("/", response_model=list[ProductPublic])
async def list_products(limit: int = 50):
    docs = repo.list_products_repo({}, max(1, min(limit, 200)))
    return [ProductPublic(**d) for d in docs]


@router.get("/quotes")
async def list_quotes(limit: int = 50):
    return repo.list_quotes_repo(limit=max(1, min(limit, 200)))


@router.get("/books")
async def list_books(limit: int = 50):
    return repo.list_books_repo(limit=max(1, min(limit, 200)))


@router.get("/laptops")
async def list_laptops(limit: int = 50):
    return repo.list_laptops_repo(limit=max(1, min(limit, 200)))


# -------------------------
# SINGLE PRODUCT (dinamik)
# -------------------------
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
