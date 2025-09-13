from typing import List, Optional
from bson import ObjectId
from .database import users_col, products_col
from models.user import UserCreate
from core.security import hash_password

# --- Helpers ---
def serialize_doc(doc: dict) -> dict:
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    if "user_id" in doc and isinstance(doc["user_id"], ObjectId):
        doc["user_id"] = str(doc["user_id"])
    return doc


# --- User Repository ---
def get_user_by_email(email: str) -> Optional[dict]:
    doc = users_col.find_one({"email": email.lower()})
    return serialize_doc(doc)

def get_user_by_id(user_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    doc = users_col.find_one({"_id": oid})
    return serialize_doc(doc)

def create_user(user: UserCreate) -> dict:
    user_doc = {
        "email": user.email.lower(),
        "password_hash": hash_password(user.password),
        "full_name": user.full_name,
        "role": user.role
    }
    result = users_col.insert_one(user_doc)
    created_user = users_col.find_one({"_id": result.inserted_id})
    return serialize_doc(created_user)


# --- Product Repository (products_col) ---
def create_product_repo(product_data: dict) -> dict:
    result = products_col.insert_one(product_data)
    created_product = products_col.find_one({"_id": result.inserted_id})
    return serialize_doc(created_product)

def list_products_repo(query: dict, limit: int) -> List[dict]:
    docs = products_col.find(query).limit(limit)
    return [serialize_doc(d) for d in docs]

def find_product_by_id_repo(product_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(product_id)
    except Exception:
        return None
    doc = products_col.find_one({"_id": oid})
    return serialize_doc(doc)

def update_product_repo(product_id: str, update_data: dict) -> Optional[dict]:
    try:
        oid = ObjectId(product_id)
    except Exception:
        return None
    products_col.update_one({"_id": oid}, {"$set": update_data})
    doc = products_col.find_one({"_id": oid})
    return serialize_doc(doc)

def delete_product_repo(product_id: str) -> bool:
    try:
        oid = ObjectId(product_id)
    except Exception:
        return False
    result = products_col.delete_one({"_id": oid})
    return result.deleted_count > 0


# --- Scraper Repositories (filter by source) ---
def list_quotes_repo(limit: int = 100):
    docs = products_col.find({"source": "quotes"}).limit(limit)
    return [serialize_doc(d) for d in docs]

def list_books_repo(limit: int = 100):
    docs = products_col.find({"source": "books"}).limit(limit)
    return [serialize_doc(d) for d in docs]

def list_laptops_repo(limit: int = 100):
    docs = products_col.find({"source": "laptops"}).limit(limit)
    return [serialize_doc(d) for d in docs]
