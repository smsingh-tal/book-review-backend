#!/usr/bin/env python
"""
fix_book_data.py - Script to update missing ISBN and genre data for books in the database
"""
import random
from sqlalchemy.orm import sessionmaker
from app.db.models import Book
from app.db.session import engine

def generate_isbn():
    """Generate a random 13-digit ISBN"""
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

def get_default_genres(title, author):
    """Assign default genres based on book title or author"""
    # Simple genre assignment logic
    genres = ["Fiction"]
    
    title_lower = title.lower()
    author_lower = author.lower()
    
    # Science Fiction
    if any(keyword in title_lower for keyword in ["1984", "neuromancer", "dune", "ubik"]):
        genres.append("Science Fiction")
    
    # Mystery
    if any(keyword in title_lower for keyword in ["murder", "kill", "spy", "cold"]):
        genres.append("Mystery")
    
    # Fantasy    
    if "tolkien" in author_lower or "rings" in title_lower:
        genres.append("Fantasy")
        
    # Classic Literature
    if any(author in author_lower for author in ["austen", "dickens", "woolf", "joyce", "orwell"]):
        genres.append("Classic")
    
    return genres

def main():
    """Main function to update all books with missing data"""
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all books
        books = session.query(Book).all()
        print(f"Found {len(books)} books in database")
        
        updated_count = 0
        
        # Update each book
        for book in books:
            needs_update = False
            
            if not book.isbn:
                book.isbn = generate_isbn()
                needs_update = True
                print(f"Added ISBN for book: {book.title}")
            
            if not book.genres:
                book.genres = get_default_genres(book.title, book.author)
                needs_update = True
                print(f"Added genres for book: {book.title} - {book.genres}")
            
            if needs_update:
                updated_count += 1
        
        # Commit the changes
        session.commit()
        print(f"Successfully updated {updated_count} books")
        
        # Verify all books have genres and ISBN now
        null_isbn_count = session.query(Book).filter(Book.isbn == None).count()
        null_genres_count = session.query(Book).filter(Book.genres == None).count()
        
        print(f"Books with null ISBN: {null_isbn_count}")
        print(f"Books with null genres: {null_genres_count}")
        
        # Show a sample of books with their data
        sample_books = session.query(Book).limit(5).all()
        print("\nSample of updated books:")
        for book in sample_books:
            print(f"ID: {book.id}, Title: {book.title}, Author: {book.author}")
            print(f"  ISBN: {book.isbn}")
            print(f"  Genres: {book.genres}")
            print()
            
    except Exception as e:
        print(f"Error updating books: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
