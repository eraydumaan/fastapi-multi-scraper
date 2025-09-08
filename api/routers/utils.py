# api/routers/utils.py

from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException
from datetime import datetime, timezone

from models.user import UserPublic
from api.dependencies import get_current_admin_user
from db.database import products_col

# Scraper fonksiyonlarını import ediyoruz
from services.scraper.books_scraper import scrape_books
from services.scraper.quotes_scraper import scrape_quotes
from services.scraper.laptops_scraper import scrape_laptops

router = APIRouter(prefix="/utils", tags=["Utilities"])

# --- ANA SCRAPER ENDPOINT'İ ---
@router.post("/scrape/{source}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_scrape(
    source: str,
    background_tasks: BackgroundTasks,
    current_user: UserPublic = Depends(get_current_admin_user)
):
    """
    URL'den gelen 'source' ismine göre ilgili scraper'ı arka planda çalıştırır.
    """
    scraper_tasks = {
        "books": scrape_books,
        "quotes": scrape_quotes,
        "laptops": scrape_laptops
    }
    
    task = scraper_tasks.get(source.lower())
    if not task:
        raise HTTPException(status_code=404, detail=f"Source '{source}' not found. Available sources are: {list(scraper_tasks.keys())}")

    background_tasks.add_task(task, user_id=str(current_user.id))
    return {"message": f"Scraping for '{source}' has been started in the background."}


# --- GEÇİCİ DEBUG ENDPOINT'İ ---
@router.post("/test-db-write", tags=["Utilities"])
async def test_db_write():
    """
    SADECE DEBUG AMAÇLI: Veritabanına yazma işleminin çalışıp çalışmadığını test eder.
    """
    try:
        test_record = {
            "title": "TEST KAYDI",
            "source": "test",
            "link": "#",
            "user_id": None, 
            "created_at": datetime.now(timezone.utc)
        }
        result = products_col.insert_one(test_record)
        return {
            "message": "SUCCESS: Test record inserted.",
            "inserted_id": str(result.inserted_id)
        }
    except Exception as e:
        # Hata olursa, hatanın kendisini döndürelim
        return {
            "message": "ERROR: Failed to write to database.",
            "error_details": str(e)
        }