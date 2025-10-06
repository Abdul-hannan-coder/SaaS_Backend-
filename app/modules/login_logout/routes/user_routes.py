"""
Authentication routes for user management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from ..models.user_model import UserSignUp, UserSignUpRequest, UserSignIn, UserResponse
from ..controllers.user_controller import (
    create_user_controller,
    login_user,
    get_user_by_id,
    get_all_users,
    update_user_controller,
    delete_user_controller,
    get_current_user
)
from ..models.error_models import UserNotFoundError
from ....utils.database_dependency import get_database_session
from ....utils.my_logger import get_logger
from sqlmodel import Session

logger = get_logger("AUTH_ROUTES")

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()



@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignUpRequest, db: Session = Depends(get_database_session)):
    """
    Create a new user account
    
    - **email**: User's email address (must be unique)
    - **username**: User's username (must be unique)
    - **full_name**: User's full name
    - **password**: User's password (will be hashed)
    """
    logger.info(f"Signup request received for email: {user_data.email}")
    return create_user_controller(user_data, db)

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: UserSignIn, db: Session = Depends(get_database_session)):
    """
    Login user and get access token
    
    - **email**: User's email address
    - **password**: User's password
    """
    logger.info(f"Login request received for email: {user_data.email}")
    return login_user(user_data, db)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserSignUp = Depends(get_current_user)):
    """
    Get current user information
    
    Requires authentication via Bearer token
    """
    logger.info(f"Current user info request for: {current_user.username}")
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: UserSignUp = Depends(get_current_user), db: Session = Depends(get_database_session)):
    """
    Get all users (admin function)
    
    Requires authentication via Bearer token
    """
    logger.info(f"Get all users request from: {current_user.username}")
    return get_all_users(db)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: UserSignUp = Depends(get_current_user), db: Session = Depends(get_database_session)):
    """
    Get user by ID
    
    Requires authentication via Bearer token
    """
    logger.info(f"Get user request for ID: {user_id} from: {current_user.username}")
    user = get_user_by_id(user_id, db)
    if not user:
        user_not_found_error = UserNotFoundError("User not found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
               detail=user_not_found_error.error_detail.to_dict()
        )
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_info(
    user_id: str, 
    user_data: dict, 
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update user information
    
    Requires authentication via Bearer token
    """
    logger.info(f"Update user request for ID: {user_id} from: {current_user.username}")
    return update_user_controller(user_id, user_data, db)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    user_id: str, 
    current_user: UserSignUp = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Delete user account
    
    Requires authentication via Bearer token
    """
    logger.info(f"Delete user request for ID: {user_id} from: {current_user.username}")
    delete_user_controller(user_id, db)
    return None 