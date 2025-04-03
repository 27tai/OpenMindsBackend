from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.db.database import get_db
from app.db.models import User, TestPaper
from app.api.schemas.test_paper import TestPaperCreate, TestPaperUpdate, TestPaperResponse
from app.api.schemas.result import ResultResponse
from app.api.routes.auth import get_current_admin, get_current_user
from app.services.test_paper_service import (
    create_new_test_paper,
    get_test_paper_by_id,
    get_all_test_papers,
    update_test_paper,
    delete_test_paper
)
from app.services.result_service import submit_test_and_calculate_score

# Create router
router = APIRouter(prefix="/test-papers", tags=["Test Papers"])

@router.post("/", response_model=TestPaperResponse, status_code=status.HTTP_201_CREATED)
async def create_test_paper(
    test_paper_data: TestPaperCreate, 
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Create a new test paper (admin only)
    """
    return create_new_test_paper(db=db, test_paper_data=test_paper_data)

@router.get("/", response_model=List[TestPaperResponse])
async def get_test_papers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all test papers (authenticated users only)
    """
    return get_all_test_papers(db=db)

@router.get("/{test_paper_id}", response_model=TestPaperResponse)
async def get_test_paper(
    test_paper_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific test paper by ID (authenticated users only)
    """
    test_paper = get_test_paper_by_id(db=db, test_paper_id=test_paper_id)
    if not test_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test paper not found"
        )
    return test_paper

@router.post("/{test_paper_id}/submit", response_model=ResultResponse)
async def submit_test(
    test_paper_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit answers for a test paper and get the calculated score
    
    This endpoint:
    1. Takes user answers for questions in the test paper
    2. Calculates the score based on correct answers
    3. Stores the result in the database
    """
    # Log the incoming data
    print(f"Received submission data: {data}")
    
    # Check if test paper exists
    test_paper = get_test_paper_by_id(db=db, test_paper_id=test_paper_id)
    if not test_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test paper not found"
        )
    
    # Extract user_answers from the request body
    user_answers = data
    
    try:
        result = submit_test_and_calculate_score(
            db=db, 
            user_id=current_user.id,
            test_paper_id=test_paper_id,
            user_answers=user_answers
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error occurred during test submission"
            )
        
        return result
    except Exception as e:
        print(f"Error in submit_test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing test submission: {str(e)}"
        )

@router.put("/{test_paper_id}", response_model=TestPaperResponse)
async def update_test_paper_by_id(
    test_paper_id: int,
    test_paper_data: TestPaperUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update a test paper (admin only)
    """
    test_paper = update_test_paper(db=db, test_paper_id=test_paper_id, test_paper_data=test_paper_data)
    if not test_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test paper not found"
        )
    return test_paper

@router.delete("/{test_paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_paper_by_id(
    test_paper_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a test paper (admin only)
    """
    success = delete_test_paper(db=db, test_paper_id=test_paper_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test paper not found"
        )
    return None 