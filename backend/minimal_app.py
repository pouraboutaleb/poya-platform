"""Minimal working FastAPI backend"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Poya Platform API",
    description="Manufacturing Resource and Digital Planning Operations Logistics Core Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:3000",
        "https://*.app.github.dev",
        "https://*.preview.app.github.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Poya Platform API", 
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Poya Platform API",
        "database": "sqlite (ready)",
        "timestamp": "2025-08-03"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "active",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/status"
        ]
    }
