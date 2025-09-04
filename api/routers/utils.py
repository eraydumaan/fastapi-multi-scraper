# api/routers/utils.py

from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException
from models.user import UserPublic
from api.dependencies import get_current_admin_user

# Düzeltilmiş import satırları (artık doğru ve kısa isimleri kullanıyoruz)
from services.scraper.books_scraper import scrape_books
from services.scraper.quotes_scraper import scrape_quotes

router = APIRouter(prefix="/utils", tags=["Utilities"])

@router.post("/scrape/{source}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_scrape(
    source: str,
    background_tasks: BackgroundTasks,
    current_user: UserPublic = Depends(get_current_admin_user)
):
    # Bu sözlük, gelen isteği doğru fonksiyona yönlendirir
    scraper_tasks = {
        "books": scrape_books,
        "quotes": scrape_quotes
    }
    
    task = scraper_tasks.get(source.lower())
    if not task:
        raise HTTPException(status_code=404, detail=f"Kaynak '{source}' bulunamadı. Mevcut kaynaklar: {list(scraper_tasks.keys())}")

    background_tasks.add_task(task, user_id=str(current_user.id))
    return {"message": f"'{source}' için veri kazıma işlemi arka planda başlatıldı."}