import httpx
from datetime import datetime,timezone
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO,format ="%(asctime)s - %(levelname)s - %(message)s")

async def fetch_html(url:str,client:httpx.AsyncClient,retries:int=3):
    """
    Verilen URL'den HTML içeriğini çeker. Hata olursa belirli sayıda tekrar eder.
    """
    for attempt in range(retries):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
        except httpx.RequestError as exc:
            logging.error(f"[Attempt {attempt+1}] HTTP error for {url}: {exc}")
            if attempt == retries -1:
                return None
            

def build_record(user_id,source: str,extra: dict):
    """
    ortak kayıt sablonu:kaynak,kullanici,timestamp ekler.
    """

    return {
        "source":source,
        "user_id":ObjectId(user_id),
        "created_at":datetime.now(timezone.utc),
        **extra
    }



                                        
            
