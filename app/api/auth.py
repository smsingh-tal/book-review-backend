from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from datetime import timezone
from typing import Dict, Any, Union, Optional
import json

from app.core.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    get_current_user
)
from app.db.session import get_db
from app.db.models import User, InvalidatedToken

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

from pydantic import BaseModel

class UserRegister(BaseModel):
    name: str
    username: str
    password: str

from fastapi import Body

class RegisterResponse(Token):
    message: str

@router.post("/register", response_model=RegisterResponse)
async def register(
    user: Optional[UserRegister] = None,
    name: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Register a new user using either JSON or form data."""
    try:
        # Get credentials from either JSON body or form data
        if user:
            name = user.name
            username = user.username
            password = user.password
        elif not (name and username and password):
            raise HTTPException(
                status_code=400,
                detail="Provide name, username and password as JSON or form data"
            )
            
        # Check if email already exists
        existing_user = (
            db.query(User)
            .filter(User.email == username)
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
            
        # Create new user
        password_hash = get_password_hash(password)
        new_user = User(
            name=name,
            email=username,
            hashed_password=password_hash,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_user)
        
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error creating user - database error"
            )
        
        # Create access token for the new user (auto-login)
        access_token = create_access_token(
            data={"sub": new_user.email}, 
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "message": "User created successfully",
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register/json", response_model=RegisterResponse)
async def register_json(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user using JSON data."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    try:
        password_hash = get_password_hash(user.password)
        new_user = User(
            name=user.name,
            email=user.username,
            hashed_password=password_hash,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.email}, 
            expires_delta=access_token_expires
        )
        
        return {
            "message": "User created successfully",
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def register_user(user_data: Dict[str, str], db: Session):
    """Internal function to handle user registration."""
    # Log the registration request
    print(f"Registration request received for user: {user_data['username']} (name: {user_data.get('name')})")  # Debug log
    # Debug database connection
    try:
        from app.core.config import get_settings
        from sqlalchemy import text
        print(f"Database URL: {get_settings().DATABASE_URL}")
        result = db.execute(text("SELECT 1")).scalar()
        print(f"Database connection test result: {result}")
    except Exception as e:
        import traceback
        print(f"Database connection error: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data['username']).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        password_hash = get_password_hash(user_data['password'])
        new_user = User(
            name=user_data['name'],
            email=user_data['username'],
            hashed_password=password_hash
        )
        
        # Save user to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": new_user.email}
        )
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "user": {
                "email": new_user.email,
                "id": new_user.id
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not register user. Please try again."
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return token."""
    try:
        # Use selective loading to only get required fields
        user = db.query(User.email, User.hashed_password).filter(User.email == form_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user by invalidating their token."""
    # Add token to invalidated tokens table
    invalid_token = InvalidatedToken(
        token=token,
        invalidated_at=datetime.now(timezone.utc)
    )
    db.add(invalid_token)
    db.commit()
    return {"message": "Successfully logged out"}

from app.core.auth import get_current_user  # Import from core

@router.get("/me", response_model=Dict[str, Any])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at
    }

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating the current token.
    This adds the token to the invalidated tokens table.
    """
    try:
        # Check if token is already invalidated
        existing_invalidated = db.query(InvalidatedToken).filter(
            InvalidatedToken.token == token
        ).first()
        
        if existing_invalidated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token already invalidated"
            )
        
        # Add token to invalidated tokens table
        invalidated_token = InvalidatedToken(
            token=token,
            invalidated_at=datetime.now(timezone.utc)
        )
        db.add(invalidated_token)
        db.commit()
        
        return {"message": "Successfully logged out"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}"
        )
