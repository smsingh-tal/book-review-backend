import pytest
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import get_settings

def test_database_connectivity():
    """Test database connectivity and configuration"""
    # Get database settings
    settings = get_settings()
    print(f"\nUsing DATABASE_URL: {settings.DATABASE_URL}")
    
    # Get a database session
    db = next(get_db())
    try:
        # Check current database connection info
        result = db.execute(text("SELECT current_database(), current_user, current_schema"))
        db_name, user, schema = result.fetchone()
        print(f"Connected to database: {db_name} as user: {user} using schema: {schema}")
        
        # Check search_path
        result = db.execute(text("SHOW search_path"))
        search_path = result.scalar()
        print(f"Current search_path: {search_path}")
        
        # List all schemas
        result = db.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
        """))
        schemas = [row[0] for row in result]
        print(f"Available schemas: {schemas}")
        
        # List tables in current schema
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_schema()
        """))
        tables = [row[0] for row in result]
        print(f"Tables in current schema: {tables}")
        
        # Try to query books table with explicit schema
        result = db.execute(text("SELECT COUNT(*) FROM public.books"))
        count = result.scalar()
        print(f"Books count (with explicit schema): {count}")
        
        if count > 0:
            # Get sample books
            result = db.execute(text("SELECT id, title, author FROM public.books LIMIT 3"))
            books = result.fetchall()
            print("Sample books:")
            for book in books:
                print(f"  {book.id}: {book.title} by {book.author}")
        
        # Verify we can actually see the data
        assert count > 0, "No books found in database"
        
    finally:
        db.close()
