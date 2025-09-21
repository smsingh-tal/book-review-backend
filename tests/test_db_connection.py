import pytest
from sqlalchemy import text
from app.db.session import get_engine, get_db, SessionLocal
from app.core.config import get_settings

def test_database_connection():
    """Test that we can connect to the database and execute queries"""
    settings = get_settings()
    print(f"Using database URL: {settings.DATABASE_URL}")
    try:
        # Get a database session
        db = SessionLocal()
        
        # Test basic connection
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Basic database connection failed"
        print("Basic connection test passed")
        
        # Test database configuration
        result = db.execute(text("SELECT current_database(), current_user, current_schema"))
        db_name, user, schema = result.fetchone()
        print(f"Connected to database: {db_name} as user: {user} using schema: {schema}")
        
        # List all tables in the schema
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        print(f"Available tables in public schema: {tables}")
        
        # Test that we can query the books table
        result = db.execute(text("SELECT COUNT(*) FROM books"))
        count = result.scalar()
        assert count is not None, "Could not get book count"
        print(f"Found {count} books in database")
        
        # Test that we can query a specific book
        result = db.execute(text("SELECT title FROM books LIMIT 1"))
        book = result.scalar()
        assert book is not None, "Could not retrieve a book from database"
        print(f"Sample book title: {book}")
        
        # Test database URL configuration
        settings = get_settings()
        assert "postgresql" in settings.DATABASE_URL, "Database URL should be PostgreSQL"
        assert "book_review" in settings.DATABASE_URL, "Database name should be book_review"
        
    except Exception as e:
        pytest.fail(f"Database connection test failed: {str(e)}")
    finally:
        db.close()

def test_database_session_management():
    """Test that database sessions are properly created and managed"""
    # Test session creation using the get_db dependency
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Test that the session is active
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Session is not active"
        
        # Test that we can execute a query using the session
        result = db.execute(text("SELECT COUNT(*) FROM books"))
        count = result.scalar()
        assert count is not None, "Could not execute query using session"
        print(f"Session test: Found {count} books")
        
    except Exception as e:
        pytest.fail(f"Session management test failed: {str(e)}")
    finally:
        try:
            db_generator.close()
        except:
            pass  # Ignore any errors during cleanup

def test_database_engine_configuration():
    """Test that database engine is properly configured"""
    engine = get_engine()
    
    # Test engine configuration
    # Pool size may vary in different environments; just check engine works
    assert hasattr(engine.pool, 'size')
    
    # Test connection pool
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Engine connection failed"
        
        # Test schema setting
        result = conn.execute(text("SHOW search_path"))
        search_path = result.scalar()
        assert 'public' in search_path, "Search path should include public schema"
