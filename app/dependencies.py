"""
FastAPI dependencies for PrimeHaul OS
Provides reusable dependency injection for database sessions, authentication, and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.auth import decode_access_token
from app.models import User, Company


def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get the currently authenticated user

    Args:
        access_token: JWT token from HTTP-only cookie
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If user is not authenticated or token is invalid

    Usage:
        @app.get("/endpoint")
        def handler(current_user: User = Depends(get_current_user)):
            # current_user is authenticated User object
            pass
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(access_token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Update last login timestamp
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()

    return user


def get_optional_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    FastAPI dependency to optionally get the current user
    Returns None if not authenticated instead of raising exception

    Args:
        access_token: JWT token from HTTP-only cookie
        db: Database session

    Returns:
        User object if authenticated, None otherwise

    Usage:
        @app.get("/endpoint")
        def handler(current_user: Optional[User] = Depends(get_optional_current_user)):
            if current_user:
                # User is authenticated
                pass
            else:
                # Anonymous user
                pass
    """
    if not access_token:
        return None

    try:
        payload = decode_access_token(access_token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        return user
    except JWTError:
        return None


def require_role(required_role: str):
    """
    Dependency factory to require a specific role

    Args:
        required_role: Role required (owner, admin, member)

    Returns:
        Dependency function that checks user role

    Usage:
        @app.post("/endpoint")
        def handler(current_user: User = Depends(require_role("admin"))):
            # current_user has at least 'admin' role
            pass
    """
    role_hierarchy = {
        "owner": 3,
        "admin": 2,
        "member": 1
    }

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role, 0)

        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )

        return current_user

    return role_checker


def get_current_company(current_user: User = Depends(get_current_user)) -> Company:
    """
    FastAPI dependency to get the current user's company

    Args:
        current_user: Current authenticated user

    Returns:
        Company object

    Usage:
        @app.get("/endpoint")
        def handler(company: Company = Depends(get_current_company)):
            # company is the current user's company
            pass
    """
    return current_user.company


def verify_company_access(company_slug: str, current_user: User = Depends(get_current_user)) -> Company:
    """
    Dependency to verify user has access to a specific company by slug

    Args:
        company_slug: Company slug from URL
        current_user: Current authenticated user

    Returns:
        Company object

    Raises:
        HTTPException: If user doesn't belong to the company

    Usage:
        @app.get("/{company_slug}/admin/dashboard")
        def handler(
            company_slug: str,
            company: Company = Depends(verify_company_access)
        ):
            # company matches the slug and user has access
            pass
    """
    if current_user.company.slug != company_slug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    return current_user.company
