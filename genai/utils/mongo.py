from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "genai")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Usage: from genai.utils.mongo import db 