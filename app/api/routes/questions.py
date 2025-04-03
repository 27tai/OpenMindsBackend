from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.models import User, Question
from app.api.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.api.routes.auth import get_current_admin, get_current_user
from app.services.question_service import (
    create_new_question,
    get_question_by_id,
    get_all_questions,
    get_questions_by_test_paper,
    update_question,
    delete_question
)

# Create router
router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new question (admin only)
    """
    return create_new_question(db=db, question_data=question_data)

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    test_paper_id: Optional[int] = Query(None, description="Filter by test paper ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all questions or filter by test paper ID (authenticated users only)
    """
    if test_paper_id:
        return get_questions_by_test_paper(db=db, test_paper_id=test_paper_id)
    return get_all_questions(db=db)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific question by ID (authenticated users only)
    """
    question = get_question_by_id(db=db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question_by_id(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a question (admin only)
    """
    question = update_question(db=db, question_id=question_id, question_data=question_data)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_by_id(
    question_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a question (admin only)
    """
    success = delete_question(db=db, question_id=question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return None 