import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import claims

# Load environment variables
os.environ["GOOGLE_API_KEY"] = "AIzaSyCClaQFo9MrwLwbhv1ryZ21neeQbEyN41A"

app = FastAPI(
    title="GenAI API",
    description="GenAI Service API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to GenAI API",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "genai",
        "version": "1.0.0"
    } 