"""
Authentication router for user signup, login, and logout.
Maintains backward compatibility with customer-based endpoints.
"""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..auth import create_access_token, generate_session_id, verify_password
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.post("/signup", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: schemas.UserSignup,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    Creates a new user with the 'customer' role by default.

    Args:
        user_data: User signup information including username, password, and email.
        request: The HTTP request object to extract IP address.
        db: Database session dependency.

    Returns:
        Access token and user information.

    Raises:
        HTTPException: If username or email already exists.
    """
    # Check if username already exists
    existing_user = crud.get_user_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = crud.get_user_by_email(db, email=user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with customer role
    db_user = crud.create_user(db=db, user=user_data, role=models.UserRole.CUSTOMER)

    # Generate session
    session_id = generate_session_id()
    ip_address = request.client.host if request.client else None

    # Create session record
    crud.create_user_session(
        db=db,
        user_id=db_user.id,
        session_id=session_id,
        ip_address=ip_address
    )

    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.username, "session_id": session_id, "user_id": db_user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    credentials: schemas.UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and create a new session.

    Args:
        credentials: User login credentials (username and password).
        request: The HTTP request object to extract IP address.
        db: Database session dependency.

    Returns:
        Access token and user information.

    Raises:
        HTTPException: If credentials are invalid or account is inactive.
    """
    # Verify user exists
    db_user = crud.get_user_by_username(db, username=credentials.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate new session
    session_id = generate_session_id()
    ip_address = request.client.host if request.client else None

    # Create session record
    crud.create_user_session(
        db=db,
        user_id=db_user.id,
        session_id=session_id,
        ip_address=ip_address
    )

    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.username, "session_id": session_id, "user_id": db_user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.post("/logout", response_model=schemas.LogoutResponse)
def logout(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    End a user session (logout).

    Args:
        session_id: The session ID to terminate.
        db: Database session dependency.

    Returns:
        Logout confirmation with session details.

    Raises:
        HTTPException: If session not found or already ended.
    """
    # End the session
    db_session = crud.end_user_session(db, session_id=session_id)

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already ended"
        )

    return {
        "message": "Successfully logged out",
        "session_id": session_id,
        "logout_time": db_session.logout_time
    }


@router.get("/sessions/{user_id}", response_model=List[schemas.UserSessionResponse])
def get_user_sessions(
    user_id: int,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all sessions for a user.

    Args:
        user_id: The ID of the user.
        active_only: If True, only return active sessions.
        db: Database session dependency.

    Returns:
        List of user sessions.

    Raises:
        HTTPException: If user not found.
    """
    # Verify user exists
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get sessions
    sessions = crud.get_user_sessions(
        db=db,
        user_id=user_id,
        active_only=active_only
    )

    return sessions

