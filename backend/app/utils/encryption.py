from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import base64
import hashlib

load_dotenv()

class EncryptionService:
    def __init__(self):
        # Generate a key from the SECRET_KEY
        secret_key = os.getenv("SECRET_KEY", "default-secret-key-change-this")
        # Derive a proper Fernet key from the secret
        key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        """Encrypt a string and return bytes"""
        if not data:
            return b""
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt bytes and return string"""
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data).decode()

# Singleton instance
encryption_service = EncryptionService()
