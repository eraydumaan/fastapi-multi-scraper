import httpx
from bs4 import BeautifulSoup
import logging

from .base_scraper import fetch_html, build_record
from db.database import products_col

async def scrape_laptops(user_id: str):
    url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
    base_url = "https://webscraper.io"
    all_laptops_data = []
    
    logging.info("Scraping for 'laptops' started...")

    async with httpx.AsyncClient(timeout=20.0) as client:
        html_content = await fetch_html(url, client)

        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            products = soup.find_all("div", class_="thumbnail")

            for product in products:
                try:
                    title_tag = product.find("a", class_="title")
                    price_tag = product.find("h4", class_="price")
                    # DÜZELTME: Yanlış olan 'pull-right' yerine doğru class adı olan 'review-count' kullanıyoruz.
                    stock_tag = product.find("p", class_="review-count")

                    if not all([title_tag, price_tag, stock_tag]):
                        logging.warning("A product with missing data was skipped.")
                        continue

                    price_str = price_tag.text.strip().lstrip('$')
                    
                    laptop_details = {
                        "title": title_tag['title'],
                        "price": float(price_str),
                        "stock": stock_tag.text.strip(), # Buraya da .strip() eklemek her zaman iyidir.
                        "link": base_url + title_tag['href']
                    }
                    
                    record = build_record(user_id, source="laptops", extra=laptop_details)
                    all_laptops_data.append(record)
                
                except (AttributeError, KeyError, ValueError) as e:
                    logging.error(f"Could not parse a product, skipping. Error: {e}")
        else:
            logging.error("HTML content could not be fetched for laptops.")

    if all_laptops_data:
        products_col.insert_many(all_laptops_data)
        
    logging.info(f"Scraping for 'laptops' finished. Inserted {len(all_laptops_data)} new laptops.")