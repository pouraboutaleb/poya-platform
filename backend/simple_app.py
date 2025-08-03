"""
Minimal FastAPI Application for E2E Testing
This is a simplified version without complex dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="MRDPOL Core API",
    description="ERP Platform for Production Management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to MRDPOL Core API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mrdpol-core-api"}

@app.get("/api/v1/warehouse/warehouse-requests")
async def get_warehouse_requests():
    """Mock warehouse requests endpoint"""
    return {
        "status": "success",
        "data": [],
        "message": "Warehouse requests endpoint is working"
    }

@app.post("/api/v1/warehouse/warehouse-requests")
async def create_warehouse_request():
    """Mock create warehouse request endpoint"""
    return {
        "status": "success",
        "id": 1,
        "message": "Warehouse request created successfully"
    }

@app.get("/api/v1/orders")
async def get_orders():
    """Mock orders endpoint"""
    return {
        "status": "success",
        "data": [],
        "message": "Orders endpoint is working"
    }

@app.post("/api/v1/orders")
async def create_order():
    """Mock create order endpoint"""
    return {
        "status": "success",
        "id": 1,
        "message": "Order created successfully"
    }

@app.get("/api/v1/route-cards")
async def get_route_cards():
    """Mock route cards endpoint"""
    return {
        "status": "success",
        "data": [],
        "message": "Route cards endpoint is working"
    }

@app.post("/api/v1/route-cards")
async def create_route_card():
    """Mock create route card endpoint"""
    return {
        "status": "success",
        "id": 1,
        "message": "Route card created successfully"
    }

@app.post("/api/v1/auth/login")
async def login():
    """Mock login endpoint"""
    return {
        "status": "success",
        "token": "mock_token_12345",
        "message": "Login endpoint is working"
    }

@app.get("/api/v1/items")
async def get_items():
    """Mock items endpoint"""
    return {
        "status": "success",
        "data": [
            {"id": 1, "name": "Test Item 1", "code": "ITEM001"},
            {"id": 2, "name": "Test Item 2", "code": "ITEM002"}
        ],
        "message": "Items endpoint is working"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
