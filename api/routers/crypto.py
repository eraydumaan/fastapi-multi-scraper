from fastapi import APIRouter, Depends, HTTPException
import httpx
import logging
from api.dependencies import get_current_user

router = APIRouter(prefix="/crypto", tags=["Crypto"])

COINGECKO_API = "https://api.coingecko.com/api/v3"

# 🔥 Top 10 coin
@router.get("/top")
async def get_top_coins(user=Depends(get_current_user)):
    url = f"{COINGECKO_API}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)
            logging.info(f"[TOP COINS] Status={res.status_code} Body={res.text}")
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logging.exception("❌ CoinGecko Top Coins request failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{coin_id}")
async def get_coin_detail(coin_id: str, user=Depends(get_current_user)):
    url = f"{COINGECKO_API}/coins/{coin_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            logging.info(f"[COIN DETAIL] Status={res.status_code} Body={res.text}")
            res.raise_for_status()
            return res.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logging.exception("❌ CoinGecko Coin Detail request failed")
        raise HTTPException(status_code=500, detail=str(e))
