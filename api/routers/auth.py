# api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

# MODELLER
from models.user import UserCreate, UserPublic
from models.token import Token

# GÜVENLİK VE VERİTABANI
from core.security import verify_password, create_access_token
from db import repository as repo

# AUTH DEPENDENCY
from api.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    try:
        created_user = repo.create_user(user_data)
        return UserPublic(**created_user)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Kullanıcı email + şifre ile giriş yapar.
    access_token ve token_type döner.
    """
    user = repo.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Token payload (sub = user_id, email = user email)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: UserPublic = Depends(get_current_user)):
    """
    Kullanıcının kendi bilgilerini döner (token ile erişilir).
    """
    return current_user
