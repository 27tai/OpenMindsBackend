from datetime import datetime, timedelta
from typing import Optional
import os
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

# JWT Settings (from environment variables with defaults)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-placeholder-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data (dict): The data to encode in the JWT
        expires_delta (Optional[timedelta], optional): Token expiration time. Defaults to None.
        
    Returns:
        str: JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token (str): The JWT token to verify
        
    Returns:
        Optional[dict]: The decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None 