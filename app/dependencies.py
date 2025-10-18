"""
Authorization dependencies for FastAPI endpoints.

Provides dependency functions for:
- Extracting current user from JWT token
- Checking user roles and permissions
- Protecting endpoints with role-based access control
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import crud, models
from .auth import SECRET_KEY, ALGORITHM
from .database import get_db

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Extract and validate the current user from the JWT token.
    
    Args:
        credentials: The HTTP Bearer token credentials.
        db: Database session dependency.
    
    Returns:
        The authenticated User model instance.
    
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    if user_id:
        user = crud.get_user(db, user_id=user_id)
    else:
        user = crud.get_user_by_username(db, username=username)
    
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get the current active user.
    
    This is an alias for get_current_user for backward compatibility
    and semantic clarity.
    
    Args:
        current_user: The current user from get_current_user dependency.
    
    Returns:
        The authenticated active User model instance.
    """
    return current_user


async def require_superadmin(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Require that the current user is a superadmin.
    
    Use this dependency to protect endpoints that should only be
    accessible to superadmins.
    
    Args:
        current_user: The current user from get_current_user dependency.
    
    Returns:
        The authenticated superadmin User model instance.
    
    Raises:
        HTTPException: If user is not a superadmin (403 Forbidden).
    """
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user


async def require_admin(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Require that the current user is an admin or superadmin.
    
    Use this dependency to protect endpoints that should only be
    accessible to admins and superadmins.
    
    Args:
        current_user: The current user from get_current_user dependency.
    
    Returns:
        The authenticated admin/superadmin User model instance.
    
    Raises:
        HTTPException: If user is not an admin or superadmin (403 Forbidden).
    """
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_role(required_role: models.UserRole):
    """
    Factory function to create a dependency that requires a specific role.
    
    Example usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(models.UserRole.ADMIN))])
        def admin_endpoint():
            return {"message": "Admin access granted"}
    
    Args:
        required_role: The role required to access the endpoint.
    
    Returns:
        A dependency function that checks for the required role.
    """
    async def role_checker(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role != required_role and not current_user.is_superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' required"
            )
        return current_user
    
    return role_checker


def require_any_role(*roles: models.UserRole):
    """
    Factory function to create a dependency that requires any of the specified roles.
    
    Example usage:
        @router.get("/staff-only", dependencies=[Depends(require_any_role(
            models.UserRole.ADMIN, models.UserRole.SUPERADMIN
        ))])
        def staff_endpoint():
            return {"message": "Staff access granted"}
    
    Args:
        *roles: Variable number of roles, any of which grants access.
    
    Returns:
        A dependency function that checks for any of the required roles.
    """
    async def role_checker(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role not in roles and not current_user.is_superadmin:
            role_names = ", ".join([r.value for r in roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of the following roles required: {role_names}"
            )
        return current_user
    
    return role_checker

