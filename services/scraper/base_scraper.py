import httpx
from datetime import datetime, timezone
from bson import ObjectId
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def fetch_html(url: str, client: httpx.AsyncClient, retries: int = 3):
    """
    Verilen URL'den HTML içeriğini çeker. 
    404 durumunda None döner, diğer hatalarda retry dener.
    """
    for attempt in range(retries):
        try:
            response = await client.get(url)
            if response.status_code == 404:   # ✅ 404 = içerik yok
                logging.info(f"Page not found (404): {url}")
                return None
            response.raise_for_status()
            return response.content
        except httpx.RequestError as exc:
            logging.error(f"[Attempt {attempt+1}] HTTP error for {url}: {exc}")
            if attempt == retries - 1:
                return None


def build_record(user_id, source: str, extra: dict):
    """
    Ortak kayıt şablonu: kaynak, kullanıcı, timestamp ekler.
    user_id None veya geçersizse, kayıt null user_id ile kaydedilir.
    """
    user_obj_id = None
    try:
        if user_id:
            user_obj_id = ObjectId(user_id)
    except Exception:
        user_obj_id = None

    return {
        "source": source,
        "user_id": user_obj_id,
        "created_at": datetime.now(timezone.utc),
        **extra
    }
