from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "deepverify_logs")

class MongoDB:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            cls.client = MongoClient(MONGODB_URL)
            cls.db = cls.client[MONGODB_DB]
        return cls.db

    @classmethod
    def get_collection(cls, collection_name):
        db = cls.connect()
        return db[collection_name]

# Collections
def get_ai_logs():
    return MongoDB.get_collection("ai_logs")

def get_audit_logs():
    return MongoDB.get_collection("audit_logs")
