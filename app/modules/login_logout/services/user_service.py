"""
User service with consolidated business logic
"""
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
from ..models.user_model import UserSignUp, UserSignUpRequest, UserResponse
from ..models.error_models import UserNotFoundError, UserAlreadyExistsError, DatabaseError
from ..services.auth_service import get_password_hash
from ....utils.my_logger import get_logger

logger = get_logger("USER_SERVICE")

# Core service functions - simplified and consolidated

def create_user(user_data: UserSignUpRequest, db: Session) -> UserResponse:
    """Create a new user with business logic validation"""
    # Check if user already exists (only email needs to be unique)
    existing_user = db.exec(select(UserSignUp).where(UserSignUp.email == user_data.email)).first()
    if existing_user:
        raise UserAlreadyExistsError("Email already registered", email=user_data.email)
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user = UserSignUp(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password=hashed_password
    )
    
    # Database operations
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created successfully: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error creating user: {str(e)}", operation="create_user", error_type="transaction")

def get_user_by_id(user_id: str, db: Session) -> Optional[UserResponse]:
    """Get user by ID"""
    try:
        user_uuid = UUID(user_id)
        user = db.exec(select(UserSignUp).where(UserSignUp.id == user_uuid)).first()
        
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except ValueError:
        raise UserNotFoundError("Invalid user ID format")
    except Exception as e:
        raise DatabaseError(f"Error getting user by ID: {str(e)}", operation="get_user_by_id", error_type="query")

def get_user_by_email(email: str, db: Session) -> Optional[UserSignUp]:
    """Get user by email"""
    try:
        return db.exec(select(UserSignUp).where(UserSignUp.email == email)).first()
    except Exception as e:
        raise DatabaseError(f"Error getting user by email: {str(e)}", operation="get_user_by_email", error_type="query")

def get_user_by_username(username: str, db: Session) -> Optional[UserSignUp]:
    """Get user by username"""
    try:
        return db.exec(select(UserSignUp).where(UserSignUp.username == username)).first()
    except Exception as e:
        raise DatabaseError(f"Error getting user by username: {str(e)}", operation="get_user_by_username", error_type="query")

def get_all_users(db: Session) -> List[UserResponse]:
    """Get all users"""
    try:
        users = db.exec(select(UserSignUp)).all()
        return [
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
    except Exception as e:
        raise DatabaseError(f"Error retrieving users: {str(e)}", operation="get_all_users", error_type="query")

def update_user(user_id: str, user_data: dict, db: Session) -> UserResponse:
    """Update user with business logic validation"""
    try:
        user_uuid = UUID(user_id)
        user = db.exec(select(UserSignUp).where(UserSignUp.id == user_uuid)).first()
        
        if not user:
            raise UserNotFoundError("User not found", user_id=user_id)
        
        # Update fields
        for field, value in user_data.items():
            if hasattr(user, field) and field not in ["id", "password"]:
                setattr(user, field, value)
        
        # Update timestamp and save
        user.updated_at = datetime.utcnow()
        
        # Database operations
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated successfully: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except ValueError:
        raise UserNotFoundError("Invalid user ID format")
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error updating user: {str(e)}", operation="update_user", error_type="transaction")

def delete_user(user_id: str, db: Session) -> bool:
    """Delete user with business logic validation"""
    try:
        user_uuid = UUID(user_id)
        user = db.exec(select(UserSignUp).where(UserSignUp.id == user_uuid)).first()
        
        if not user:
            raise UserNotFoundError("User not found", user_id=user_id)
        
        # Database operations
        db.delete(user)
        db.commit()
        
        logger.info(f"User deleted successfully: {user.email}")
        return True
        
    except ValueError:
        raise UserNotFoundError("Invalid user ID format")
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Error deleting user: {str(e)}", operation="delete_user", error_type="transaction")
