from pymongo import MongoClient
from core.settings import get_settings

settings = get_settings()
client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

def set_validators():
    print("🚀 Applying schema validators...")

    # Products koleksiyonu için schema
    product_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [ "source", "created_at"],
            "properties": {
                "name": {"bsonType": "string"},
                "price": {"bsonType": ["double", "int", "null"]},
                "source": {"bsonType": "string"},
                "created_at": {"bsonType": "date"},
            },
        }
    }
    db.command("collMod", "products", validator=product_validator, validationLevel="moderate")

    # Users koleksiyonu için schema
    user_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["email", "username", "hashed_password", "role"],
            "properties": {
                "email": {"bsonType": "string"},
                "username": {"bsonType": "string"},
                "hashed_password": {"bsonType": "string"},
                "role": {"enum": ["user", "admin"]},
            },
        }
    }
    db.command("collMod", "users", validator=user_validator, validationLevel="moderate")

    print("✅ Validators applied")

if __name__ == "__main__":
    set_validators()
