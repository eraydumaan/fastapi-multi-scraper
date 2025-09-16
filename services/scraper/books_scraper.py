import httpx
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from .base_scraper import fetch_html, build_record
from db.database import products_col

async def scrape_books(user_id: str):
    """
    books.toscrape.com sitesindeki tüm kitapları çeker ve veritabanına kaydeder.
    """
    current_page = 1
    inserted_count = 0
    updated_count = 0

    logging.info("Scraping for 'books' started...")
    async with httpx.AsyncClient(timeout=20.0) as client:
        while True:
            # 🔑 Doğru URL formatı
            full_url = f"http://books.toscrape.com/catalogue/page-{current_page}.html"
            logging.info(f"Scraping page {current_page}: {full_url}")

            content = await fetch_html(full_url, client)
            if not content:
                logging.info("No more pages found. Stopping...")
                break

            soup = BeautifulSoup(content, "html.parser")
            books = soup.find_all("article", class_="product_pod")

            if not books:   # ✅ Kitap yoksa loop'u kır
                logging.info("No books on this page. Stopping...")
                break

            for book in books:
                title = book.h3.a["title"]
                link = "http://books.toscrape.com/catalogue/" + book.h3.a["href"]
                price = float(book.find("p", class_="price_color").text.replace("£", ""))
                stock = book.find("p", class_="instock availability").text.strip()

                record = build_record(user_id, "books", {
                    "product_id": link,
                    "name": title,
                    "price": price,
                    "stock": stock,
                    "link": link,
                    "created_at": datetime.utcnow()
                })

                result = products_col.update_one(
                    {"product_id": record["product_id"]},
                    {"$set": record},
                    upsert=True
                )
                if result.upserted_id:
                    inserted_count += 1
                elif result.modified_count > 0:
                    updated_count += 1

            # ❌ 50. sayfadan sonra 51'e geçmeye çalışma
            current_page += 1

    logging.info(
        f"Scraping for 'books' finished. Inserted {inserted_count} new, Updated {updated_count} existing books."
    )
