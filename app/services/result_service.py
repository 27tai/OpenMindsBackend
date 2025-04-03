from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional, List
import json

from app.db.models import Result, TestPaper, Question
from app.api.schemas.result import ResultCreate, ResultUpdate

def create_new_result(db: Session, result_data: ResultCreate) -> Result:
    """
    Create a new result
    
    Args:
        db (Session): Database session
        result_data (ResultCreate): Result data
        
    Returns:
        Result: Created result
    """
    try:
        # Create result
        new_result = Result(
            user_id=result_data.user_id,
            test_paper_id=result_data.test_paper_id,
            final_score=result_data.final_score,
            user_answers=json.dumps(result_data.user_answers) if result_data.user_answers else None
        )
        
        # Add to database
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        
        return new_result
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error creating result: {str(e)}")
        return None

def get_result_by_id(db: Session, result_id: int) -> Optional[Result]:
    """
    Get result by ID
    
    Args:
        db (Session): Database session
        result_id (int): Result ID
        
    Returns:
        Optional[Result]: Result if found, None otherwise
    """
    result = db.query(Result).filter(Result.id == result_id).first()
    if result:
        # Parse JSON field
        if result.user_answers and isinstance(result.user_answers, str):
            result.user_answers = json.loads(result.user_answers)
    return result

def get_results_by_user(db: Session, user_id: int) -> List[Result]:
    """
    Get results by user ID
    
    Args:
        db (Session): Database session
        user_id (int): User ID
        
    Returns:
        List[Result]: List of results for the user
    """
    results = db.query(Result).filter(Result.user_id == user_id).all()
    
    # Parse JSON fields
    for result in results:
        if result.user_answers and isinstance(result.user_answers, str):
            result.user_answers = json.loads(result.user_answers)
    
    return results

def get_results_by_test_paper(db: Session, test_paper_id: int) -> List[Result]:
    """
    Get results by test paper ID
    
    Args:
        db (Session): Database session
        test_paper_id (int): Test paper ID
        
    Returns:
        List[Result]: List of results for the test paper
    """
    results = db.query(Result).filter(Result.test_paper_id == test_paper_id).all()
    
    # Parse JSON fields
    for result in results:
        if result.user_answers and isinstance(result.user_answers, str):
            result.user_answers = json.loads(result.user_answers)
    
    return results

def update_result(db: Session, result_id: int, result_data: ResultUpdate) -> Optional[Result]:
    """
    Update result
    
    Args:
        db (Session): Database session
        result_id (int): Result ID
        result_data (ResultUpdate): Result data to update
        
    Returns:
        Optional[Result]: Updated result if found, None otherwise
    """
    try:
        # Get result
        result = db.query(Result).filter(Result.id == result_id).first()
        if not result:
            return None
            
        # Update fields
        if result_data.final_score is not None:
            result.final_score = result_data.final_score
            
        if result_data.user_answers is not None:
            result.user_answers = json.dumps(result_data.user_answers)
            
        # Commit changes
        db.commit()
        db.refresh(result)
        
        # Parse JSON fields for return
        if result.user_answers and isinstance(result.user_answers, str):
            result.user_answers = json.loads(result.user_answers)
            
        return result
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error updating result: {str(e)}")
        return None

def submit_test_and_calculate_score(db: Session, user_id: int, test_paper_id: int, user_answers: Dict[str, Any]) -> Optional[Result]:
    """
    Submit a test with user answers and calculate the final score
    
    Args:
        db (Session): Database session
        user_id (int): User ID
        test_paper_id (int): Test paper ID
        user_answers (Dict[str, Any]): Dictionary of question IDs to user answers
        
    Returns:
        Optional[Result]: Created result with calculated score
    """
    try:
        print(f"Processing submission for user {user_id}, test {test_paper_id}")
        print(f"User answers data: {user_answers}")
        
        # Get test paper
        test_paper = db.query(TestPaper).filter(TestPaper.id == test_paper_id).first()
        if not test_paper:
            print(f"Test paper with ID {test_paper_id} not found")
            return None
        
        # Get all questions for this test paper
        questions = db.query(Question).filter(Question.test_paper_id == test_paper_id).all()
        print(f"Found {len(questions)} questions for test paper {test_paper_id}")
        
        if not questions:
            print(f"No questions found for test paper with ID {test_paper_id}")
            return None
        
        # Extract user_answers from the request data if it's nested
        answer_data = {}
        
        # Handle both formats: direct dict or nested under 'user_answers'
        if isinstance(user_answers, dict):
            if 'user_answers' in user_answers:
                answer_data = user_answers['user_answers']
            else:
                answer_data = user_answers
        
        print(f"Normalized answer data: {answer_data}")
        
        # Calculate score
        total_score = 0.0
        max_possible_score = sum(q.max_score for q in questions)
        print(f"Max possible score: {max_possible_score}")
        
        for question in questions:
            question_id = str(question.id)
            
            # Skip if question not answered
            if question_id not in answer_data:
                print(f"Question {question_id} not answered")
                continue
            
            user_answer = answer_data[question_id]
            print(f"Question {question_id}: user answered {user_answer}")
            
            # Print question details for debugging
            print(f"Question {question_id} details: correct_option_index={question.correct_option_index}, options={question.options}")
            print(f"question options {question.options}")
            # Process the answer based on option format
            if question.options:
                
                if user_answer == question.correct_option_index:
                    print("running 1st if block")
                    print(f"Answer is correct! Adding {question.max_score} points")
                    total_score += question.max_score
                else:
                    print(f"Answer is incorrect. Expected index {question.correct_option_index}, got {user_answer}")
                # for i, option in enumerate(question.options):
                #     print(f"Checking option {i}: {option}")
                #     # Handle different option formats
                #     option_id = None
                #     if isinstance(option, dict) and 'id' in option:
                #         print("running 2st if block")
                #         option_id = option['id']
                #         print(f"Option ID: {option_id}")
                    
                #     # Check if this is the selected option
                #     if option_id is not None and str(option_id) == str(user_answer):
                        
                #         print(f"Found matching option at index {i}")
                #         print("running 3t if block")
                        
                #         # Check if this is the correct option
                #         if  i == question.correct_option_index:
                #             print("running 4st if block")
                #             print(f"Answer is correct! Adding {question.max_score} points")
                #             total_score += question.max_score
                #         else:
                #             print(f"Answer is incorrect. Expected index {question.correct_option_index}, got {i}")
                #         break
                print(f"Total score after question {question_id}: {total_score}")

            
            else:
                print(f"WARNING: Question {question_id} has invalid options format")
        
        # Calculate percentage score
        if max_possible_score > 0:
            percentage_score = (total_score / max_possible_score) * 100
        else:
            percentage_score = 0.0
        
        print(f"Final score: {total_score}/{max_possible_score} = {percentage_score}%")
        
        # Create result
        new_result = Result(
            user_id=user_id,
            test_paper_id=test_paper_id,
            final_score=total_score,
            user_answers=json.dumps(answer_data)
        )
        
        # Add to database
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        print(f"Created result with ID: {new_result.id}")
        
        # Parse JSON fields for return
        if new_result.user_answers and isinstance(new_result.user_answers, str):
            new_result.user_answers = json.loads(new_result.user_answers)
            
        return new_result
    except Exception as e:
        db.rollback()
        print(f"Error submitting test: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def delete_result(db: Session, result_id: int) -> bool:
    """
    Delete result
    
    Args:
        db (Session): Database session
        result_id (int): Result ID
        
    Returns:
        bool: True if deleted, False otherwise
    """
    try:
        # Get result
        result = db.query(Result).filter(Result.id == result_id).first()
        if not result:
            return False
            
        # Delete result
        db.delete(result)
        db.commit()
        
        return True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error deleting result: {str(e)}")
        return False 