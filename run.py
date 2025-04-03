import subprocess
import sys
import os
from app.db.create_tables import create_tables

def setup_database():
    """Initialize the database tables"""
    print("Setting up database...")
    success = create_tables()
    if not success:
        print("Failed to set up database. Exiting.")
        sys.exit(1)
    print("Database setup complete!")

def start_application():
    """Start the FastAPI application"""
    print("Starting MCQ Platform API...")
    try:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        print("Error: uvicorn not found. Please install it with 'pip install uvicorn'")
        sys.exit(1)

if __name__ == "__main__":
    # Set up database tables
    
    
    # Start the application
    start_application() 