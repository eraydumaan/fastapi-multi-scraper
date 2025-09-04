import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from bson import ObjectId
from db.database import products_col

async def scrape_books(user_id: str):
    """
    books.toscrape.com sitesindeki tüm kitapları çeker ve veritabanına kaydeder.
    """
    BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
    all_data = []
    
    print("Scraping for 'books' started...")
    async with httpx.AsyncClient(timeout=20.0) as client:
        for page in range(1, 51): # 50 sayfanın tamamını gezer
            url = BASE_URL.format(page)
            print(f"Scraping page {page}/50...")
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.content, "html.parser")
                products = soup.find_all("article", class_="product_pod")

                for product in products:
                    price_text = product.find("p", class_="price_color").text.strip().lstrip("£")
                    all_data.append({
                        "title": product.h3.a["title"],
                        "price": float(price_text),
                        "stock": product.find("p", class_="instock availability").text.strip(),
                        "link": "http://books.toscrape.com/catalogue/" + product.h3.a["href"],
                        "source": "books", # <-- DÜZELTME: 'source' alanı eklendi
                        "user_id": ObjectId(user_id),
                        "created_at": datetime.now(timezone.utc)
                    })
            except httpx.RequestError as exc:
                print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
                break
    
    if all_data:
        products_col.insert_many(all_data)
        
    print(f"Scraping for 'books' finished. Inserted {len(all_data)} new books.")