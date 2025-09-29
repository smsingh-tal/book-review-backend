"""Test database utilities"""
import warnings
import pytest
import asyncio
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.db.models import Base
from app.db.session import get_db
from app.main import app
from fastapi.testclient import TestClient

# Filter out passlib crypt deprecation warning
warnings.filterwarnings("ignore", message="'crypt' is deprecated", module="passlib.utils")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test database URL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/book_review_test"

@pytest.fixture(scope="session")
def engine():
    """Create database engine"""
    return create_engine(TEST_DATABASE_URL)

@pytest.fixture(scope="session", autouse=True)
def setup_database(engine):
    from tests.test_utils import populate_test_books
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Populate test data in a separate session
    Session = sessionmaker(bind=engine)
    temp_session = Session()
    try:
        populate_test_books(temp_session)
        temp_session.commit()
    except Exception:
        temp_session.rollback()
        raise
    finally:
        temp_session.close()
        
    yield engine  # Use yield instead of return
    
    # Cleanup after tests
    Base.metadata.drop_all(bind=engine)

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
def sample_data(db: Session):
    """Create sample data for tests"""
    from app.db.models import User, Book, Review, UserFavorite
    from datetime import datetime, timedelta
    
    # Create a test user
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="dummy_hash"
    )
    db.add(user)
    db.flush()
    
    # Get some books to work with
    books = db.query(Book).limit(5).all()
    
    # Create reviews and favorites for test user
    reviews = []
    for i, book in enumerate(books):
        review = Review(
            user_id=user.id,
            book_id=book.id,
            rating=4.0 + (i % 2),  # Alternate between 4.0 and 5.0
            text=f"Test review {i + 1}",
            created_at=datetime.now() - timedelta(days=i),
            updated_at=datetime.now()
        )
        reviews.append(review)
        
        if i % 2 == 0:  # Add every other book as a favorite
            favorite = UserFavorite(user_id=user.id, book_id=book.id)
            db.add(favorite)
    
    db.add_all(reviews)
    db.commit()
    
    # Return created test data
    return {
        "user": user,
        "books": books,
        "reviews": reviews
    }

@pytest.fixture
def client(db: Session) -> Generator:
    """Create a test client for the FastAPI application with test database session"""
    def _get_test_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
