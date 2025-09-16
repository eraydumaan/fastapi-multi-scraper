from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pymongo import MongoClient

from core.settings import get_settings
from core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from models.user import UserCreate, UserPublic

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Auth"])

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
users = db["users"]


@router.post("/register", response_model=UserPublic)
def register(user: UserCreate):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_doc = user.model_dump()
    user_doc["hashed_password"] = hash_password(user.password)
    del user_doc["password"]
    result = users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return UserPublic(**user_doc)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "role": user.get("role", "user"),
    }
    access_token = create_access_token(payload, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(payload)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh(token: str):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    new_access = create_access_token(payload, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": new_access, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
def me(current_user: UserPublic = Depends()):
    return current_user
