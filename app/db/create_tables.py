import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import inspect
from app.db.database import engine, Base
from app.db.models import User,  TestPaper, Question, Result

def create_tables():
    """
    Create all tables in the database if they don't exist
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"Existing tables: {', '.join(existing_tables) if existing_tables else 'None'}")
        print("Creating tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        updated_tables = inspect(engine).get_table_names()
        new_tables = set(updated_tables) - set(existing_tables)
        
        if new_tables:
            print(f"Successfully created tables: {', '.join(new_tables)}")
        else:
            print("No new tables were created. All tables may already exist.")
        
        print(f"All tables in database: {', '.join(updated_tables)}")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

if __name__ == "__main__":
    print("Initializing database tables...")
    success = create_tables()
    if success:
        print("Database initialization completed successfully.")
    else:
        print("Database initialization failed.")
        sys.exit(1) 