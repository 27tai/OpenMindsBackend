from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# Schema for option object
class OptionBase(BaseModel):
    text: str
    is_correct: bool = False

# Base Question schema with shared attributes
class QuestionBase(BaseModel):
    text: str
    test_paper_id: int
   
  
# Schema for creating a new question
class QuestionCreate(QuestionBase):
    options: List[OptionBase]
    correct_option_index: Optional[int] = None
    max_score: Optional[float] = None

# Schema for updating a question
class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    test_paper_id: Optional[int] = None
    options: Optional[List[OptionBase]] = None
    correct_option_index: Optional[int] = None
    explanation: Optional[str] = None

# Schema for option in response
class OptionResponse(BaseModel):
    id: int
    text: str
    

# Schema for returning a question (response model)
class QuestionResponse(QuestionBase):
    id: int
    options: List[OptionResponse]
    correct_option_id: int
    max_score: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True 