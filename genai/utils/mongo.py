from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variable
MONGO_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'genai')

try:
    # Create async client for FastAPI
    client = AsyncIOMotorClient(MONGO_URI)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

db = client[DB_NAME]

# Usage: from genai.utils.mongo import db 