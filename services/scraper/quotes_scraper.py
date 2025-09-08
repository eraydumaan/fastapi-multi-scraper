import httpx
from bs4 import BeautifulSoup
import logging
from .base_scraper import fetch_html, build_record
from db.database import products_col

async def scrape_quotes(user_id: str):
    """
    quotes.toscrape.com sitesindeki tüm alıntıları çeker ve veritabanına kaydeder.
    print() yerine logging kullanır.
    """
    base_url = "http://quotes.toscrape.com"
    current_url = "/page/1/"
    all_quotes_data = []
    
    logging.info("Scraping for 'quotes' started...")
    async with httpx.AsyncClient(timeout=20.0) as client:
        while current_url:
            full_url = base_url + current_url
            logging.info(f"Scraping page: {full_url}")

            content = await fetch_html(full_url, client)
            if not content:
                break

            soup = BeautifulSoup(content, "html.parser")
            quotes = soup.find_all("div", class_="quote")

            for quote in quotes:
                text = quote.find("span", class_="text").text.strip()
                author = quote.find("small", class_="author").text.strip()
                author_link = quote.find("a")["href"]

                record = build_record(user_id, "quotes", {
                    "title": f'"{text}" - {author}',
                    "price": None,
                    "stock": "N/A",
                    "link": base_url + author_link
                })
                all_quotes_data.append(record)
            
            next_li = soup.find("li", class_="next")
            current_url = next_li.find("a")["href"] if next_li else None
    
    if all_quotes_data:
        products_col.insert_many(all_quotes_data)
        
    logging.info(f"Scraping for 'quotes' finished. Inserted {len(all_quotes_data)} new quotes.")