import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_test_database():
    try:
        # Connect to default database
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cur = conn.cursor()
        
        # Drop database if exists
        cur.execute("DROP DATABASE IF EXISTS book_review_test")
        
        # Create database
        cur.execute("CREATE DATABASE book_review_test")
        
        # Close connection
        cur.close()
        conn.close()
        print("Test database created successfully!")
        
    except Exception as e:
        print(f"Error creating test database: {str(e)}")
        raise

if __name__ == "__main__":
    create_test_database()
