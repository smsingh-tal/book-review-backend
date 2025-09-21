from typing import List, Optional
import logging
from fastapi import HTTPException
from sqlalchemy import or_, func, text
from sqlalchemy.orm import Session
from app.db.models import Book
from app.schemas.book import BookCreate, BookUpdate, BookSearchParams

logger = logging.getLogger(__name__)

class BookService:
    def __init__(self, db: Session):
        self.db = db

    def get_book(self, book_id: int) -> Optional[Book]:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_books(self, params: BookSearchParams) -> tuple[List[Book], int]:
        logger.info("Fetching books with params: %s", params)
        
        # First verify we can access the books table directly
        try:
            result = self.db.execute(text("SELECT COUNT(*) FROM books"))
            count = result.scalar()
            logger.info(f"Direct SQL count from books table: {count}")
            
            # Get sample books directly
            result = self.db.execute(text("SELECT id, title FROM books LIMIT 3"))
            books = result.fetchall()
            if books:
                logger.info("Sample books from direct SQL:")
                for book in books:
                    logger.info(f"  Book {book.id}: {book.title}")
            else:
                logger.warning("No sample books found in direct SQL query")
        except Exception as e:
            logger.error(f"Error in direct SQL query: {str(e)}")
        
        # Start the SQLAlchemy query
        query = self.db.query(Book)
        logger.info(f"Initial SQLAlchemy query: {str(query)}")
        
        # Apply search filter if search parameter exists
        if params.search:
            search = f"%{params.search}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search),
                    Book.author.ilike(search)
                ))
                
        # Get total count before sorting and pagination
        total_count = query.count()
        
        # Apply sorting
        if params.sort_by:
            # Map frontend sort fields to database columns
            column_mapping = {
                'title': Book.title,
                'author': Book.author,
                'rating': Book.average_rating,
                'average_rating': Book.average_rating,
                'total_reviews': Book.total_reviews,
                'date': Book.publication_date,
                'publication_date': Book.publication_date
            }
            
            # Get the correct column to sort by
            sort_column = column_mapping.get(params.sort_by)
            if sort_column is None:
                logger.warning(f"Unknown sort column: {params.sort_by}")
            else:
                logger.info(f"Sorting by column: {params.sort_by} -> {sort_column}")
                
                # Always ensure sort_order is either 'asc' or 'desc'
                sort_order = params.sort_order.lower() if params.sort_order else 'asc'
                if sort_order not in ['asc', 'desc']:
                    sort_order = 'asc'
                
                # Apply the sort order
                logger.info(f"Applying {sort_order.upper()} order")
                if sort_order == 'desc':
                    sort_column = sort_column.desc()
                else:
                    sort_column = sort_column.asc()
                
                # Clear any existing order_by and apply the new one
                query = query.order_by(None)  # Clear existing order_by
                query = query.order_by(sort_column)
                
                # Log the final query with sort clause for debugging
                logger.info(f"Query after sorting: {query}")
        
        # Apply pagination with defaults
        if params.offset is not None and params.limit is not None:
            # Use offset/limit style pagination
            query = query.offset(params.offset).limit(params.limit)
        else:
            # Use page/items_per_page style pagination with defaults
            page = params.page if params.page is not None else 1
            items_per_page = params.items_per_page if params.items_per_page is not None else 50
            query = query.offset((page - 1) * items_per_page).limit(items_per_page)
        
        result = query.all()
        print(f"Total count: {total_count}, Results: {len(result)}")
        print(f"First few results: {[book.title for book in result[:3]]}")
        return result, total_count

    def create_book(self, book_data: BookCreate) -> Book:
        db_book = Book(**book_data.model_dump())
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def update_book(self, book_id: int, book_data: BookUpdate) -> Optional[Book]:
        db_book = self.get_book(book_id)
        if not db_book:
            return None
            
        update_data = book_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_book, field, value)
            
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def delete_book(self, book_id: int) -> bool:
        db_book = self.get_book(book_id)
        if not db_book:
            return False
            
        self.db.delete(db_book)
        self.db.commit()
        return True

    def update_book_rating(self, book_id: int, new_rating: int) -> Optional[Book]:
        """
        Update book's average rating and total reviews when a new review is added
        """
        db_book = self.get_book(book_id)
        if not db_book:
            return None

        current_total = db_book.total_reviews
        current_average = float(db_book.average_rating or 0)
        
        # Calculate new average and round to 1 decimal
        new_total = current_total + 1
        new_average = round(((current_average * current_total) + new_rating) / new_total, 1)
        
        db_book.average_rating = new_average
        db_book.total_reviews = new_total
        
        self.db.commit()
        self.db.refresh(db_book)
        return db_book
