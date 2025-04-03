from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

# Schema for submitting answers
class TestSubmission(BaseModel):
    user_id: int
    test_paper_id: int
    user_answers: Dict[str, Any]  # Dictionary of question IDs to user answers

# Base Result schema with shared attributes
class ResultBase(BaseModel):
    user_id: int
    test_paper_id: int
    final_score: float = 0.0
    user_answers: Optional[Dict[str, Any]] = None

# Schema for creating a new result
class ResultCreate(ResultBase):
    user_id: int
    test_paper_id: int
    final_score: float = 0.0
    user_answers: Optional[Dict[str, Any]] = None

# Schema for updating a result
class ResultUpdate(BaseModel):
    final_score: Optional[float] = None
    user_answers: Optional[Dict[str, Any]] = None

# Schema for returning a result (response model)
class ResultResponse(ResultBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True 