from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from app.db.models import UserRole
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    email: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6)

class AdminCreate(UserCreate):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6)
    admin_secret: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None

    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d') if v else None
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    email: EmailStr
    role: UserRole 

class UserUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=15)
    date_of_birth: datetime = Field(...)  # Change to datetime type

    @validator('date_of_birth', pre=True)
    def parse_date(cls, value):
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Invalid date format, use YYYY-MM-DD')
        return value

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d')
        }

class UserUpdateResponse(UserBase):
    id: int
    full_name: str
    email: EmailStr
    phone_number: str
    date_of_birth: datetime  # Change to datetime type
    role: UserRole
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d')
        }

# AdminCreateUser - simplified model for admin to create users
class AdminCreateUser(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    # No full_name field required - backend will generate a default