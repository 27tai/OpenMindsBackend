from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any, Union
import json

from app.db.models import Question, TestPaper
from app.api.schemas.question import QuestionCreate, QuestionUpdate

def create_new_question(db: Session, question_data: QuestionCreate) -> Question:
    """
    Create a new question
    
    Args:
        db (Session): Database session
        question_data (QuestionCreate): Question data
        
    Returns:
        Question: Created question
    """
    try:
        # Format options data
        options = []
        correct_option_index = None
        
        for i, option in enumerate(question_data.options):
            option_data = {"text": option.text}
            
            # If this option is marked as correct, update correct_option_index
            if option.is_correct:
                correct_option_index = i if question_data.correct_option_index is None else question_data.correct_option_index
                
            options.append(option_data)
        
        # Create question
        new_question = Question(
            question_text=question_data.text,
            test_paper_id=question_data.test_paper_id,
            options=json.dumps(options),
            correct_option_index=correct_option_index,
            max_score=question_data.max_score
        )
        
        # Add to database
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        
        return format_question_output(new_question, db)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error creating question: {str(e)}")
        return None

def get_all_questions(db: Session) -> List[Question]:
    """
    Get all questions
    
    Args:
        db (Session): Database session
        
    Returns:
        List[Question]: List of all questions
    """
    questions = db.query(Question).all()
    return [format_question_output(q, db) for q in questions]

def get_questions_by_test_paper(db: Session, test_paper_id: int) -> List[Question]:
    """
    Get questions by test paper ID
    
    Args:
        db (Session): Database session
        test_paper_id (int): Test paper ID
        
    Returns:
        List[Question]: List of questions for the test paper
    """
    questions = db.query(Question).filter(
        Question.test_paper_id == test_paper_id
    ).all()
    
    return [format_question_output(q, db) for q in questions]


def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
    """
    Get question by ID
    
    Args:
        db (Session): Database session
        question_id (int): Question ID
        
    Returns:
        Optional[Question]: Question if found, None otherwise
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if question:
        return format_question_output(question, db)
        
    return None

def update_question(db: Session, question_id: int, question_data: QuestionUpdate) -> Optional[Question]:
    """
    Update question
    
    Args:
        db (Session): Database session
        question_id (int): Question ID
        question_data (QuestionUpdate): Question data to update
        
    Returns:
        Optional[Question]: Updated question if found, None otherwise
    """
    try:
        # Get question
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None
            
        # Update fields
        if question_data.text is not None:
            question.question_text = question_data.text
            
        if question_data.test_paper_id is not None:
            question.test_paper_id = question_data.test_paper_id
            
        if question_data.difficulty is not None:
            question.difficulty = question_data.difficulty.value
            
        if question_data.explanation is not None:
            question.explanation = question_data.explanation
        
        # If options are provided, update them
        if question_data.options is not None:
            options = []
            correct_option_index = None
            
            for i, option in enumerate(question_data.options):
                option_data = {"text": option.text}
                
                # If this option is marked as correct, update correct_option_index
                if option.is_correct:
                    correct_option_index = i if question_data.correct_option_index is None else question_data.correct_option_index
                    
                options.append(option_data)
            
            question.options = json.dumps(options)
            
            if correct_option_index is not None:
                question.correct_option_index = correct_option_index
        
        # Commit changes
        db.commit()
        db.refresh(question)
        
        return format_question_output(question, db)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error updating question: {str(e)}")
        return None

def delete_question(db: Session, question_id: int) -> bool:
    """
    Delete question
    
    Args:
        db (Session): Database session
        question_id (int): Question ID
        
    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        # Get question
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return False
            
        # Delete question
        db.delete(question)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error deleting question: {str(e)}")
        return False

def format_question_output(question: Question, db: Session = None) -> Question:
    """
    Format question for output, converting JSON options to a more usable format
    
    Args:
        question (Question): Question from database
        db (Session, optional): Database session
        
    Returns:
        Question: Formatted question
    """
    
    # Parse options JSON
    options_data = json.loads(question.options) if isinstance(question.options, str) else question.options
    
    # Format options with IDs
    options = []
    for i, option in enumerate(options_data):
        option_id = i + 1  # Generate sequential IDs for options
        options.append({
            "id": option_id,
            "text": option["text"]
        })
    
    # Store the options on the question
    question.options = options
    
    # Set correct option ID
    if question.correct_option_index is not None and 0 <= question.correct_option_index < len(options):
        question.correct_option_id = options[question.correct_option_index]["id"]
    else:
        question.correct_option_id = None
    
    # Set text correctly
    question.text = question.question_text
    question.max_score=question.max_score
    # Add difficulty from database value
    # if hasattr(question, 'difficulty'):
    #     question.difficulty = question.difficulty
    # else:
    #     question.difficulty = "medium"  # Default
    
    return question 