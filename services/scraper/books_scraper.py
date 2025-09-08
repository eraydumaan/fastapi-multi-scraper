# wscraping/services/scraper/books_scraper.py
import httpx
from bs4 import BeautifulSoup
from db.database import products_col
from .base_scraper import fetch_html, build_record

async def scrape_books(user_id: str):
    """
    books.toscrape.com sitesindeki tüm kitapları çeker ve veritabanına kaydeder.
    """
    BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
    all_data = []
    
    print("Scraping for 'books' started...")
    async with httpx.AsyncClient(timeout=20.0) as client:
        for page in range(1, 51):  # 50 sayfa
            url = BASE_URL.format(page)
            print(f"Scraping page {page}/50...")

            content = await fetch_html(url, client)
            if not content:
                continue  # sayfada hata varsa atla

            soup = BeautifulSoup(content, "html.parser")
            products = soup.find_all("article", class_="product_pod")

            for product in products:
                price_text = product.find("p", class_="price_color").text.strip().lstrip("£")
                record = build_record(user_id, "books", {
                    "title": product.h3.a["title"],
                    "price": float(price_text),
                    "stock": product.find("p", class_="instock availability").text.strip(),
                    "link": "http://books.toscrape.com/catalogue/" + product.h3.a["href"]
                })
                all_data.append(record)
    
    if all_data:
        products_col.insert_many(all_data)
        
    print(f"Scraping for 'books' finished. Inserted {len(all_data)} new books.")
