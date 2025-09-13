from fastapi import APIRouter
from db.repository import list_quotes_repo

router = APIRouter(prefix="/quotes", tags=["Quotes"])

@router.get("/")
async def list_quotes(limit: int = 100):
    return list_quotes_repo(limit)