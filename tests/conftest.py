"""
Test fixtures for PrimeHaul OS.

Sets required env vars before importing the app, then provides
a TestClient with an in-memory SQLite database.

Uses type adapters to make PostgreSQL-specific types work with SQLite.
"""

import os
import uuid

# Set required env vars BEFORE any app imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("SUPERADMIN_PASSWORD", "TestSuperAdmin123!")
os.environ.setdefault("SALES_PASSWORD", "TestSalesPass123!")
os.environ.setdefault("DEV_DASHBOARD_PASSWORD", "TestDevPass123!")

# Patch PostgreSQL-specific types to work with SQLite
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
from sqlalchemy import String, Text, event

# Override compile for SQLite
from sqlalchemy.ext.compiler import compiles

@compiles(PG_UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"

@compiles(PG_JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.database import get_db
from app.auth import hash_password, create_access_token


# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a test database session."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def app_client(db):
    """Provide a TestClient with overridden DB dependency."""
    from app.main import app
    from starlette.testclient import TestClient

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_company(db):
    """Create a test company."""
    from app.models import Company
    company = Company(
        id=uuid.uuid4(),
        company_name="Test Removals Ltd",
        slug="test-removals",
        email="test@testremovalsltd.co.uk",
        phone="07700900123",
        subscription_status="trial",
        credits=10,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture
def test_user(db, test_company):
    """Create a test user with owner role."""
    from app.models import User
    user = User(
        id=uuid.uuid4(),
        company_id=test_company.id,
        email="owner@testremovalsltd.co.uk",
        full_name="Test Owner",
        password_hash=hash_password("TestPassword1"),
        role="owner",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user, test_company):
    """Create a valid JWT token for the test user."""
    return create_access_token(
        user_id=str(test_user.id),
        company_id=str(test_company.id),
    )


@pytest.fixture
def authenticated_client(app_client, auth_token):
    """Provide a client with auth cookie set."""
    app_client.cookies.set("access_token", auth_token)
    return app_client
