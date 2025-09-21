import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
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
        cur.execute("DROP DATABASE IF EXISTS book_review")
        
        # Create database
        cur.execute("CREATE DATABASE book_review")
        
        # Close connection
        cur.close()
        conn.close()
        print("Database created successfully!")

        # Run init_books.sql to populate the books table
        import os
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'init_books.sql')
        sql_file = os.path.abspath(sql_file)
        print(f"Running {sql_file} to populate books table...")
        exit_code = os.system(f'psql -U postgres -d book_review -f "{sql_file}"')
        if exit_code != 0:
            raise RuntimeError(f"Failed to run {sql_file} (psql exit code {exit_code})")
        print("Books table populated from init_books.sql!")
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        raise

if __name__ == "__main__":
    create_database()
