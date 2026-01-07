"""
Staging environment authentication
Adds basic HTTP auth to protect staging site from public access
"""
import os
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

# Credentials from environment variables
STAGING_USERNAME = os.getenv("STAGING_USERNAME", "primehaul")
STAGING_PASSWORD = os.getenv("STAGING_PASSWORD", "changeme123")


def verify_staging_auth(credentials: HTTPBasicCredentials) -> bool:
    """
    Verify basic auth credentials for staging environment

    Args:
        credentials: HTTP Basic Auth credentials from request

    Returns:
        True if authenticated

    Raises:
        HTTPException: If credentials are invalid
    """
    correct_username = secrets.compare_digest(credentials.username, STAGING_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, STAGING_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic realm='primehaul Staging'"},
        )

    return True
