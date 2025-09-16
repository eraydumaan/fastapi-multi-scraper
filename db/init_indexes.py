from pymongo import MongoClient, ASCENDING
from core.settings import get_settings

settings = get_settings()
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

def create_indexes():
    print("🚀 Creating indexes...")

    # Users: email & username unique
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)

    # Products: product_id unique
    db.products.create_index([("product_id", ASCENDING)], unique=True)

    # Common: created_at index
    db.products.create_index([("created_at", ASCENDING)])
    db.users.create_index([("created_at", ASCENDING)])

    print("✅ Indexes created")

if __name__ == "__main__":
    create_indexes()
