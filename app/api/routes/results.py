from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import User
from app.api.schemas.result import ResultResponse, TestSubmission
from app.api.routes.auth import get_current_user, get_current_admin
from app.services.result_service import (
    get_result_by_id,
    get_results_by_user,
    get_results_by_test_paper,
    submit_test_and_calculate_score,
    delete_result
)

# Create router
router = APIRouter(prefix="/results", tags=["Results"])

@router.post("/submit", response_model=ResultResponse)
async def submit_test(
    submission: TestSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a test with answers and calculate score
    
    This endpoint:
    1. Takes user answers for a test paper
    2. Calculates the score based on correct answers
    3. Stores the result in the database
    """
    # Ensure the user can only submit for themselves
    if submission.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit tests for your own user account"
        )
    
    result = submit_test_and_calculate_score(
        db=db, 
        user_id=submission.user_id,
        test_paper_id=submission.test_paper_id,
        user_answers=submission.user_answers
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test paper not found or error occurred during submission"
        )
    
    return result

@router.get("/my-results", response_model=List[ResultResponse])
async def get_my_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all results for the current user
    """
    return get_results_by_user(db=db, user_id=current_user.id)

@router.get("/users/{user_id}", response_model=List[ResultResponse])
async def get_user_results(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Get all results for a specific user (admin only)
    """
    return get_results_by_user(db=db, user_id=user_id)

@router.get("/test-papers/{test_paper_id}", response_model=List[ResultResponse])
async def get_test_paper_results(
    test_paper_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Get all results for a specific test paper (admin only)
    """
    return get_results_by_test_paper(db=db, test_paper_id=test_paper_id)

@router.get("/{result_id}", response_model=ResultResponse)
async def get_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific result by ID
    
    Users can only access their own results, admins can access any result
    """
    result = get_result_by_id(db=db, result_id=result_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    # Check if user is authorized to view this result
    if result.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own results"
        )
    
    return result

@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_result_by_id(
    result_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Delete a result (admin only)
    """
    success = delete_result(db=db, result_id=result_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result not found"
        )
    
    return None 