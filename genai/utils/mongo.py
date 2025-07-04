from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = """mongodb+srv://aswinraaj2405:nnOrXYpYQ7tBhKuN@genai.c2hdznk.mongodb.net/?retryWrites=true&w=majority&appName=GenAI"""
DB_NAME = "genai"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Usage: from genai.utils.mongo import db 