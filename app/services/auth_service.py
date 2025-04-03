from typing import Optional
import os
from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.models import User, UserRole
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from dotenv import load_dotenv

load_dotenv()

# Get admin secret key from environment variables
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "mcq_admin_secret_key_change_in_production")

def register_user(db: Session, full_name: str, email: str, password: str, role: UserRole = UserRole.USER) -> Optional[User]:
    """
    Register a new user
    
    Args:
        db (Session): Database session
        full_name (str): User's full name
        email (str): User's email
        password (str): User's password
        role (UserRole, optional): User's role. Defaults to UserRole.USER.
        
    Returns:
        Optional[User]: The created user or None if email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return None
    
    # Create new user
    hashed_password = hash_password(password)
    new_user = User(
        full_name=full_name,
        email=email,
        hashed_password=hashed_password,
        role=role
    )
    
    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def register_admin(db: Session, full_name: str, email: str, password: str, admin_secret: str) -> Optional[User]:
    """
    Register a new admin user
    
    Args:
        db (Session): Database session
        full_name (str): Admin's full name
        email (str): Admin's email
        password (str): Admin's password
        admin_secret (str): Secret key for admin registration
        
    Returns:
        Optional[User]: The created admin or None if email already exists or admin_secret is invalid
    """
    # Verify admin secret
    if admin_secret != ADMIN_SECRET_KEY:
        return None
    
    # Register as admin
    return register_user(db, full_name, email, password, UserRole.ADMIN)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user
    
    Args:
        db (Session): Database session
        email (str): User's email
        password (str): User's password
        
    Returns:
        Optional[User]: The authenticated user or None if authentication fails
    """
    # Get user by email
    user = db.query(User).filter(User.email == email).first()
    
    # Check user exists and password is correct
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    return user

def create_user_token(user: User) -> dict:
    """
    Create a JWT token for a user
    
    Args:
        user (User): The user to create a token for
        
    Returns:
        dict: Access token and token type
    """
    # Create token data with user ID, email, and role
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value  # Use the string value of the enum
    }
    
    # Create the actual token
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID
    
    Args:
        db (Session): Database session
        user_id (int): User ID
        
    Returns:
        Optional[User]: The user or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email
    
    Args:
        db (Session): Database session
        email (str): User email
        
    Returns:
        Optional[User]: The user or None if not found
    """
    return db.query(User).filter(User.email == email).first() 

def update_user_by_id(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    """
    Update a user by ID
    
    Args:
        db (Session): Database session
        user_id (int): User ID
        user_data (dict): User data to update
        
    Returns:
        Optional[User]: The updated user or None if not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # Convert Pydantic model to dict if needed
    update_data = user_data.dict() if hasattr(user_data, 'dict') else user_data

    # Filter out None values - don't update fields with None
    filtered_data = {k: v for k, v in update_data.items() if v is not None}

    
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        print(f"Error updating user: {str(e)}")
        raise