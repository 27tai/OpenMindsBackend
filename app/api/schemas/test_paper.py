from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Base TestPaper schema with shared attributes
class TestPaperBase(BaseModel):
    name: str
    duration_minutes: Optional[int] = 60
    is_active: Optional[bool] = True

# Schema for creating a new test paper
class TestPaperCreate(TestPaperBase):
    pass

# Schema for updating a test paper
class TestPaperUpdate(BaseModel):
    name: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

# Schema for returning a test paper (response model)
class TestPaperResponse(TestPaperBase):
    id: int
    created_at: datetime
    updated_at: datetime
    questions_count: Optional[int] = 0
    
    class Config:
        orm_mode = True 