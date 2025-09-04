import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from bson import ObjectId
from db.database import products_col

async def scrape_quotes(user_id: str):
    """
    quotes.toscrape.com sitesindeki tüm alıntıları çeker ve veritabanına kaydeder.
    """
    base_url = "http://quotes.toscrape.com"
    current_url = "/page/1/"
    all_quotes_data = []
    
    print("Scraping for 'quotes' started...")
    async with httpx.AsyncClient(timeout=20.0) as client:
        while current_url:
            full_url = base_url + current_url
            print(f"Scraping page: {full_url}")

            try:
                response = await client.get(full_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "html.parser")
                quotes = soup.find_all("div", class_="quote")

                for quote in quotes:
                    text = quote.find("span", class_="text").text.strip()
                    author = quote.find("small", class_="author").text.strip()
                    author_link = quote.find("a")["href"]

                    all_quotes_data.append({
                        "title": f'"{text}" - {author}',
                        "price": None,
                        "stock": "N/A",
                        "link": base_url + author_link,
                        "source": "quotes",
                        "user_id": ObjectId(user_id),
                        "created_at": datetime.now(timezone.utc)
                    })
                
                next_li = soup.find("li", class_="next")
                current_url = next_li.find("a")["href"] if next_li else None

            except httpx.RequestError as exc:
                print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
                break
    
    if all_quotes_data:
        products_col.insert_many(all_quotes_data)
        
    print(f"Scraping for 'quotes' finished. Inserted {len(all_quotes_data)} new quotes.")