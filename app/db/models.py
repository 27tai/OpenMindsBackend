from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, ARRAY, JSON, Enum, Boolean
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from .database import Base

class UserRole(str, enum.Enum):
    """Enum for user roles"""
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    """
    User table for storing user information
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(15), nullable=True, unique=True)
    date_of_birth = Column(TIMESTAMP, nullable=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    results = relationship("Result", back_populates="user")

class TestPaper(Base):
    """
    Test Paper table for storing test paper information
    """
    __tablename__ = "test_papers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    questions = relationship("Question", back_populates="test_paper", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="test_paper", cascade="all, delete-orphan")

class Question(Base):
    """
    Question table for storing question information
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    max_score = Column(Float, nullable=False, default=1.0)
    # Store options as JSON array since MySQL doesn't have a native ARRAY type
    options = Column(JSON, nullable=False)  # Will store array of 4 options
    correct_option_index = Column(Integer, nullable=False)  # Index of the correct option (0-3)
    test_paper_id = Column(Integer, ForeignKey("test_papers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    test_paper = relationship("TestPaper", back_populates="questions")

class Result(Base):
    """
    Results table for storing test results
    """
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    test_paper_id = Column(Integer, ForeignKey("test_papers.id", ondelete="CASCADE"), nullable=False)
    final_score = Column(Float, nullable=False, default=0.0)
    user_answers = Column(JSON, nullable=True, comment="Dictionary of question numbers and user's answers")
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="results")
    test_paper = relationship("TestPaper", back_populates="results")
