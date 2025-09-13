from pymongo import MongoClient
from core.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]   # burası düzeltildi

users_col = db["users"]
products_col = db["products"]
quotes_col = db["quotes"]
books_col = db["books"]
laptops_col = db["laptops"]

# E-posta alanının benzersiz olduğundan emin olalım
try:
    users_col.create_index("email", unique=True)
except Exception as e:
    print(f"Could not create index (might already exist): {e}")
