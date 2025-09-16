import httpx
from bs4 import BeautifulSoup
import logging
import hashlib
from datetime import datetime
from .base_scraper import fetch_html, build_record   # ✅ relative import
from db.database import products_col

async def scrape_quotes(user_id: str):
    """
    quotes.toscrape.com sitesindeki tüm alıntıları çeker ve veritabanına kaydeder.
    Aynı alıntılar duplicate olmadan upsert edilir.
    """
    base_url = "http://quotes.toscrape.com"
    current_url = "/page/1/"
    inserted_count = 0
    updated_count = 0

    logging.info("Scraping for 'quotes' started...")
    async with httpx.AsyncClient(timeout=20.0) as client:
        while current_url:
            full_url = base_url + current_url
            logging.info(f"Scraping page: {full_url}")

            content = await fetch_html(full_url, client)
            if not content:
                logging.info("No more pages found. Stopping...")
                break

            soup = BeautifulSoup(content, "html.parser")
            quotes = soup.find_all("div", class_="quote")

            if not quotes:  # ✅ hiç quote yoksa loop'u kır
                logging.info("No quotes found on this page. Stopping...")
                break

            for quote in quotes:
                text = quote.find("span", class_="text").text.strip()
                author = quote.find("small", class_="author").text.strip()
                author_link = quote.find("a")["href"]

                # 🔑 benzersiz product_id (hash)
                unique_id = hashlib.md5(f"{text}-{author}".encode("utf-8")).hexdigest()

                record = build_record(user_id, "quotes", {
                    "product_id": unique_id,
                    "name": text,
                    "title": f'"{text}" - {author}',
                    "price": None,
                    "stock": "N/A",
                    "link": base_url + author_link,
                    "created_at": datetime.utcnow(),
                })

                # ✅ Upsert → duplicate hatası olmaz
                result = products_col.update_one(
                    {"product_id": record["product_id"]},
                    {"$set": record},
                    upsert=True
                )
                if result.upserted_id:
                    inserted_count += 1
                elif result.modified_count > 0:
                    updated_count += 1

            # bir sonraki sayfa linkini bul
            next_li = soup.find("li", class_="next")
            current_url = next_li.find("a")["href"] if next_li else None

    logging.info(
        f"Scraping for 'quotes' finished. Inserted {inserted_count} new, Updated {updated_count} existing quotes."
    )
