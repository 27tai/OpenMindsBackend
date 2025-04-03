# MCQ Platform

A FastAPI backend for a Multiple Choice Questions platform.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Ensure you have the `.env` file with the database connection string:
   ```
   DATABASE_URL=mysql://user:password@host:port/database
   ```

## Running the Application

Start the application with:

```
uvicorn app.main:app --reload
```

The application will be available at http://127.0.0.1:8000

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Testing the Database Connection

There are two endpoints to test the database connection:

- `/db-test` - Tests the database connection directly
- `/db-test-session` - Tests the database connection using an SQLAlchemy session 