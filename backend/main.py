from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.api import ingest, verify, status, explain
from app.database import init_db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Deep-Verify Engine",
    description="AI-powered KYC verification system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    init_db()
    print("✓ Database initialized")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Deep-Verify Engine API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routers
from app.api import admin, auth
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(verify.router, prefix="/api", tags=["Verification"])
app.include_router(status.router, prefix="/api", tags=["Status"])
app.include_router(explain.router, prefix="/api", tags=["Explainability"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
