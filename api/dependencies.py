# api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from bson import ObjectId

from core.settings import get_settings
from core.security import decode_token
from models.user import UserPublic

settings = get_settings()

# /api prefix’i verdiğin için tokenUrl böyle olmalı
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
users = db["users"]

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    try:
        user_id = ObjectId(payload["id"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    user = users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    data = {
        "_id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "role": user.get("role", "user"),
    }
    return UserPublic(**data)

def require_role(required: str):
    def dependency(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
        role = getattr(current_user, "role", "user")
        if role != required:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user
    return dependency
