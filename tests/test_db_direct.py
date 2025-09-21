from sqlalchemy import create_engine, text
from app.core.config import get_settings
import sys

def test_db_connection():
    try:
        # Get settings from config
        settings = get_settings()
        db_url = settings.DATABASE_URL
        print(f"\nTesting connection with:")
        print(f"  Host: {settings.DB_HOST}")
        print(f"  Port: {settings.DB_PORT}")
        print(f"  Database: {settings.DB_NAME}")
        print(f"  User: {settings.DB_USER}")
        print(f"  URL: {db_url}")
        print(f"Trying to connect to: {db_url}")
        
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            # Get database info
            result = conn.execute(text("SELECT current_database(), current_user, current_schema()"))
            db_name, user, schema = result.fetchone()
            print(f"Connected to database: {db_name} as user: {user} using schema: {schema}")
            
            # Check books table
            result = conn.execute(text("SELECT COUNT(*) FROM books"))
            count = result.scalar()
            print(f"Found {count} books in database")
            
            if count > 0:
                # Get sample books
                result = conn.execute(text("SELECT id, title, author FROM books LIMIT 3"))
                print("\nSample books:")
                for row in result:
                    print(f"  {row.id}: {row.title} by {row.author}")
                    
    # No return needed for pytest tests
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing database connection using configuration from settings")
    if test_db_connection():
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")
