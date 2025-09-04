from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from core.config import settings
from db import repository as repo
from models.user import UserPublic

# Swagger UI'de Authorize kutusunu aktif hale getiren security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    """
    JWT token'i decode ederek ve veritabanından doğrulayarak geçerli kullanıcıyı döner.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # --- DÜZELTME 1: Veritabanından Kullanıcıyı Çekme ---
    # Token'dan gelen ID ile veritabanından gerçek kullanıcı kaydını buluyoruz.
    # Bu, 'ValidationError' hatasını çözer.
    user_doc = repo.get_user_by_id(user_id)
    if user_doc is None:
        raise credentials_exception
    
    # Veritabanından gelen tam ve doğru döküman ile UserPublic nesnesini oluşturuyoruz.
    return UserPublic(**user_doc)


def get_current_admin_user(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    """
    Giriş yapmış kullanıcının "admin" rolüne sahip olup olmadığını kontrol eder.
    Sadece admin kullanıcıların erişmesine izin verir.
    """
    # --- DÜZELTME 2: Rol Kontrolü ---
    # Modelimizdeki 'role' alanını kontrol ediyoruz, 'is_admin' diye bir alan yok.
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user