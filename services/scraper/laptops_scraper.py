import httpx
from bs4 import BeautifulSoup
import logging
import hashlib
from datetime import datetime
from .base_scraper import fetch_html, build_record
from db.database import products_col

async def scrape_laptops(user_id: str):
    """
    webscraper.io test sitesinden laptopları çeker ve veritabanına kaydeder.
    """
    url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
    base_url = "https://webscraper.io"
    inserted_count = 0
    updated_count = 0

    logging.info("Scraping for 'laptops' started...")

    async with httpx.AsyncClient(timeout=20.0) as client:
        html_content = await fetch_html(url, client)

        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")

            # ✅ Daha gevşek selector
            items = soup.select("div.thumbnail")
            logging.info(f"Found {len(items)} laptop items on the page")

            for item in items:
                try:
                    title_tag = item.select_one("a.title")
                    price_tag = item.select_one("h4.pull-right.price")

                    if not all([title_tag, price_tag]):
                        logging.warning("A product with missing data was skipped.")
                        continue

                    title = title_tag["title"].strip()
                    price_str = price_tag.get_text(strip=True).lstrip("$")
                    link = base_url + title_tag["href"]

                    logging.info(f"Found product: {title} | {price_str} | {link}")

                    laptop_details = {
                        "product_id": hashlib.md5(title.encode("utf-8")).hexdigest(),
                        "name": title,
                        "price": float(price_str),
                        "stock": "In stock",
                        "link": link,
                        "created_at": datetime.utcnow()
                    }

                    record = build_record(user_id, source="laptops", extra=laptop_details)
                    logging.info(f"Record to insert: {record}")

                    # ✅ Upsert → duplicate olmaz
                    result = products_col.update_one(
                        {"product_id": record["product_id"]},
                        {"$set": record},
                        upsert=True
                    )
                    if result.upserted_id:
                        inserted_count += 1
                    elif result.modified_count > 0:
                        updated_count += 1

                    logging.info(
                        f"Mongo result: matched={result.matched_count}, "
                        f"modified={result.modified_count}, "
                        f"upserted={result.upserted_id}"
                    )

                except Exception as e:
                    logging.error(f"Could not parse a product, skipping. Error: {e}")
        else:
            logging.error("HTML content could not be fetched for laptops.")

    logging.info(
        f"Scraping for 'laptops' finished. Inserted {inserted_count} new, Updated {updated_count} existing laptops."
    )
