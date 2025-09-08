import httpx
from bs4 import BeautifulSoup
import logging
from .base_scraper import fetch_html, build_record
from db.database import products_col

async def scrape_books(user_id: str):
    """
    books.toscrape.com sitesindeki tüm kitapları çeker ve veritabanına kaydeder.
    Daha sağlam bir "sonraki sayfa" mantığı ve logging kullanır.
    """
    BASE_URL = "http://books.toscrape.com/catalogue/"
    current_url = BASE_URL + "page-1.html"
    all_data = []
    page_count = 1
    
    logging.info("Scraping for 'books' started...")
    async with httpx.AsyncClient(timeout=20.0) as client:
        while current_url:
            logging.info(f"Scraping page {page_count}: {current_url}")
            content = await fetch_html(current_url, client)
            if not content:
                break

            soup = BeautifulSoup(content, "html.parser")
            products = soup.find_all("article", class_="product_pod")

            for product in products:
                record = build_record(user_id, "books", {
                    "title": product.h3.a["title"],
                    "price": float(product.find("p", class_="price_color").text.strip().lstrip("£")),
                    "stock": product.find("p", class_="instock availability").text.strip(),
                    "link": BASE_URL + product.h3.a["href"].replace("../", "")
                })
                all_data.append(record)
            
            # "Sonraki sayfa" linkini bul
            next_page_tag = soup.find("li", class_="next")
            if next_page_tag and next_page_tag.a:
                current_url = BASE_URL + next_page_tag.a["href"]
                page_count += 1
            else:
                current_url = None # Sonraki sayfa yoksa döngü durur
    
    if all_data:
        products_col.insert_many(all_data)
        
    logging.info(f"Scraping for 'books' finished. Inserted {len(all_data)} new books.")