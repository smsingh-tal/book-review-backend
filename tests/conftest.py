"""Test database utilities"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base
from app.db.session import get_db
from app.main import app
from fastapi.testclient import TestClient
from typing import Generator

# Test database URL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/book_review_test"

# Create test engine and session factory
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/book_review_test"

@pytest.fixture(scope="session")
def engine():
    """Create database engine"""
    return create_engine(TEST_DATABASE_URL)



import subprocess


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    from tests.test_utils import populate_test_books
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Populate test data in a separate session
    temp_session = SessionLocal()
    try:
        populate_test_books(temp_session)
        temp_session.commit()
    except Exception:
        temp_session.rollback()
        raise
    finally:
        temp_session.close()
    
    yield
    Base.metadata.drop_all(bind=engine)

# Provide a new DB session for each test, with rollback
@pytest.fixture(scope="function")
def db(engine):
    """Create a test database session with automatic rollback"""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    nested = connection.begin_nested()
    @event.listens_for(session, 'after_transaction_end')
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db: Session) -> Generator:
    def _get_test_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    connection.close()

@pytest.fixture
def client(db):
    """Create a test client for the FastAPI application with test database session"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.session import get_db

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    """Create a test user data"""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "username": "testuser"
    }
