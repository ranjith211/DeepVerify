import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Mock MongoDB for prototype (no actual MongoDB required)
class MockCollection:
    """Mock MongoDB collection for prototype"""
    def __init__(self):
        self.data = []
    
    def insert_one(self, document):
        """Mock insert operation"""
        document['_id'] = len(self.data) + 1
        self.data.append(document)
        return document
    
    def find_one(self, query):
        """Mock find operation"""
        for doc in self.data:
            if query.get('verification_id') == doc.get('verification_id'):
                return doc
        return None

class MongoDB:
    """Mock MongoDB client for prototype"""
    collections = {}

    @classmethod
    def connect(cls):
        """Mock connection"""
        return cls

    @classmethod
    def get_collection(cls, collection_name):
        """Get or create mock collection"""
        if collection_name not in cls.collections:
            cls.collections[collection_name] = MockCollection()
        return cls.collections[collection_name]

# Collections
def get_ai_logs():
    return MongoDB.get_collection("ai_logs")

def get_audit_logs():
    return MongoDB.get_collection("audit_logs")
