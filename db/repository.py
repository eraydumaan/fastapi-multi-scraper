from typing import List, Optional
from bson import ObjectId
from .database import users_col, products_col
from models.user import UserCreate
from core.security import hash_password

# --- User Repository ---
def get_user_by_email(email: str) -> Optional[dict]:
    return users_col.find_one({"email": email.lower()})

def get_user_by_id(user_id: str) -> Optional[dict]:
    return users_col.find_one({"_id": ObjectId(user_id)})

def create_user(user: UserCreate) -> dict:
    user_doc = {
        "email": user.email.lower(),
        "password_hash": hash_password(user.password),
        "full_name": user.full_name,
        "role": user.role
    }
    result = users_col.insert_one(user_doc)
    created_user = users_col.find_one({"_id": result.inserted_id})
    return created_user

# --- Product Repository ---
def create_product_repo(product_data: dict) -> dict:
    result = products_col.insert_one(product_data)
    return products_col.find_one({"_id": result.inserted_id})

def list_products_repo(query: dict, limit: int) -> List[dict]:
    return list(products_col.find(query).limit(limit))

def find_product_by_id_repo(product_id: str) -> Optional[dict]:
    return products_col.find_one({"_id": ObjectId(product_id)})

def update_product_repo(product_id: str, update_data: dict) -> Optional[dict]:
    products_col.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
    return find_product_by_id_repo(product_id)

def delete_product_repo(product_id: str) -> bool:
    result = products_col.delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0