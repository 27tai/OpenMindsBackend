from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db, engine
from app.api.router import router as api_router

# Create FastAPI app
app = FastAPI(
    title="MCQ Platform API",
    description="API for Multiple Choice Questions Platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/")
def read_root():
    """
    Root endpoint
    """
    return {"message": "Welcome to MCQ Platform API"}

@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    """
    Test database connection
    """
    try:
        # Execute a simple query
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {"message": "Database connection successful", "status": "ok"}
        else:
            raise HTTPException(status_code=500, detail="Database query returned unexpected result")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
