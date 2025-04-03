from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import UserRole, User
from app.services.auth_service import register_user, register_admin, authenticate_user, create_user_token, get_user_by_id, update_user_by_id
from app.utils.jwt_utils import verify_token
from app.api.schemas.auth import UserCreate, AdminCreate, UserResponse, Token, UserUpdate, UserUpdateResponse, AdminCreateUser


# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Dependency to get current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get the current authenticated user
    
    Args:
        token (str): JWT token
        db (Session): Database session
        
    Returns:
        UserResponse: Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id = int(payload.get("sub"))
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    return user

# Dependency to verify admin role
async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify the current user is an admin
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        User: Current admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def user_registration(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user_data (UserCreate): User registration data
        db (Session): Database session
        
    Returns:
        UserResponse: Created user
        
    Raises:
        HTTPException: If email already exists
    """
    new_user = register_user(
        db=db,
        full_name=user_data.full_name,
        email=user_data.email,
        password=user_data.password
    )
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return new_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    
    Args:
        form_data (OAuth2PasswordRequestForm): Username (email) and password
        db (Session): Database session
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user (username is email in our case)
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token = create_user_token(user)
    
    return token

@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """
    Get the current authenticated user's profile
    
    Args:
        current_user (UserResponse): Current authenticated user
        
    Returns:
        UserResponse: User profile
    """
    return current_user

@router.post("/admin/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def admin_registration(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """
    Register a new admin
    
    Args:
        admin_data (AdminCreate): Admin registration data with secret key
        db (Session): Database session
        
    Returns:
        UserResponse: Created admin
        
    Raises:
        HTTPException: If email already exists or admin secret is invalid
    """
    new_admin = register_admin(
        db=db,
        full_name=admin_data.full_name,
        email=admin_data.email,
        password=admin_data.password,
        admin_secret=admin_data.admin_secret
    )
    
    if not new_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin registration failed. Check email availability and admin secret."
        )
    
    return new_admin

@router.get("/admin/me", response_model=UserResponse)
async def get_admin_profile(current_admin: UserResponse = Depends(get_current_admin)):
    """
    Get the current admin's profile
    
    Args:
        current_admin (UserResponse): Current authenticated admin
        
    Returns:
        UserResponse: Admin profile
    """
    return current_admin 

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id_endpoint(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    # Only allow admins or the user themselves to access their data
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.patch("/users/{user_id}", response_model=UserUpdateResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update user profile
    
    Args:
        user_id (int): User ID
        user_data (UserUpdate): User data to update
        db (Session): Database session
        current_user (UserResponse): Current authenticated user
        
    Returns:
        UserUpdateResponse: Updated user profile
        
    Raises:
        HTTPException: If user not found or not authorized
    """
    # Only allow admins or the user themselves to update their data
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's data"
        )
    
    # Update user in database
    updated_user = update_user_by_id(db, user_id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

# Create a new endpoint for admin to create users
@router.post("/admin/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    user_data: AdminCreateUser, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Ensures only admins can access this endpoint
):
    """
    Allow admins to create new users with minimal information
    
    Args:
        user_data (UserCreate): User data containing email, password and full_name
        db (Session): Database session
        current_admin: Current authenticated admin user
        
    Returns:
        UserResponse: Created user
        
    Raises:
        HTTPException: If email already exists
    """
    # Create the user
    new_user = register_user(
        db=db,
        full_name=user_data.full_name,
        email=user_data.email,
        password=user_data.password
    )
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered or user creation failed"
        )
    
    return new_user