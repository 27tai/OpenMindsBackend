import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.db.database import engine


def migrate_add_user_fields():
    """
    Add 'phone_number' and 'date_of_birth' columns to the users table
    """
    try:
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'users'"))
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                print("Users table does not exist yet, skipping migration")
                return True
            
            # Check if phone_number column exists
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'phone_number'"))
            phone_number_exists = result.fetchone() is not None
            
            if not phone_number_exists:
                print("Adding 'phone_number' column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(15) UNIQUE"))
                print("Column 'phone_number' added successfully")
            else:
                print("Column 'phone_number' already exists, skipping")
            
            # Check if date_of_birth column exists
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'date_of_birth'"))
            date_of_birth_exists = result.fetchone() is not None
            
            if not date_of_birth_exists:
                print("Adding 'date_of_birth' column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN date_of_birth TIMESTAMP"))
                print("Column 'date_of_birth' added successfully")
            else:
                print("Column 'date_of_birth' already exists, skipping")
            
            conn.commit()
        
        return True
    except Exception as e:
        print(f"Error during migration: {e}")
        return False


if __name__ == "__main__":
    print("Running database migrations...")
    
    # Run migration
    user_fields_success = migrate_add_user_fields()
    
    if user_fields_success:
        print("Migration completed successfully.")
    else:
        print("Migration failed.")
        sys.exit(1)