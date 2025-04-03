from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from typing import List, Optional, Dict, Any

from app.db.models import TestPaper, Question
from app.api.schemas.test_paper import TestPaperCreate, TestPaperUpdate

def create_new_test_paper(db: Session, test_paper_data: TestPaperCreate) -> TestPaper:
    """
    Create a new test paper
    
    Args:
        db (Session): Database session
        test_paper_data (TestPaperCreate): Test paper data
        
    Returns:
        TestPaper: Created test paper
    """
    try:
        # Create test paper
        new_test_paper = TestPaper(
            name=test_paper_data.name,
            duration_minutes=test_paper_data.duration_minutes,
            is_active=test_paper_data.is_active
        )
        
        # Add to database
        db.add(new_test_paper)
        db.commit()
        db.refresh(new_test_paper)
        
        return new_test_paper
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error creating test paper: {str(e)}")
        return None

def get_all_test_papers(db: Session) -> List[TestPaper]:
    """
    Get all test papers with question count
    
    Args:
        db (Session): Database session
        
    Returns:
        List[TestPaper]: List of all test papers
    """
    # Query test papers with a subquery to count related questions
    papers = db.query(TestPaper).all()
    
    # Count questions for each paper
    for paper in papers:
        paper.questions_count = db.query(func.count(Question.id)).filter(
            Question.test_paper_id == paper.id
        ).scalar()
        
    return papers

def get_test_papers_by_category(db: Session, category: str) -> List[TestPaper]:
    """
    Get test papers by category 
    
    Args:
        db (Session): Database session
        category (str): Category name
        
    Returns:
        List[TestPaper]: List of test papers with the given category
    """
    # Since we've removed the category field, this function will just return all test papers
    # This is to maintain API compatibility until the frontend is updated
    return get_all_test_papers(db)

def get_test_paper_by_id(db: Session, test_paper_id: int) -> Optional[TestPaper]:
    """
    Get test paper by ID
    
    Args:
        db (Session): Database session
        test_paper_id (int): Test paper ID
        
    Returns:
        Optional[TestPaper]: Test paper if found, None otherwise
    """
    paper = db.query(TestPaper).filter(TestPaper.id == test_paper_id).first()
    
    if paper:
        paper.questions_count = db.query(func.count(Question.id)).filter(
            Question.test_paper_id == paper.id
        ).scalar()
        
    return paper

def update_test_paper(db: Session, test_paper_id: int, test_paper_data: TestPaperUpdate) -> Optional[TestPaper]:
    """
    Update test paper
    
    Args:
        db (Session): Database session
        test_paper_id (int): Test paper ID
        test_paper_data (TestPaperUpdate): Test paper data to update
        
    Returns:
        Optional[TestPaper]: Updated test paper if found, None otherwise
    """
    try:
        # Get test paper
        test_paper = get_test_paper_by_id(db, test_paper_id)
        if not test_paper:
            return None
            
        # Update fields
        if test_paper_data.name is not None:
            test_paper.name = test_paper_data.name
            
        if test_paper_data.duration_minutes is not None:
            test_paper.duration_minutes = test_paper_data.duration_minutes
            
        if test_paper_data.is_active is not None:
            test_paper.is_active = test_paper_data.is_active
            
        # Commit changes
        db.commit()
        db.refresh(test_paper)
        
        return test_paper
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error updating test paper: {str(e)}")
        return None

def delete_test_paper(db: Session, test_paper_id: int) -> bool:
    """
    Delete test paper
    
    Args:
        db (Session): Database session
        test_paper_id (int): Test paper ID
        
    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        # Get test paper
        test_paper = get_test_paper_by_id(db, test_paper_id)
        if not test_paper:
            return False
            
        # Delete test paper (cascade will take care of related questions)
        db.delete(test_paper)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error deleting test paper: {str(e)}")
        return False 