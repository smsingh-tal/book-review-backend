from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.book import Book, BookCreate, BookUpdate, BookSearchParams, BookListResponse
from app.services.book import BookService

router = APIRouter(tags=["books"])

@router.get("/", response_model=BookListResponse)
def list_books(
    search: Optional[str] = Query(None, description="Search text to filter books by title, author, or genres"),
    sortBy: Optional[str] = Query(None, description="Field to sort by (title, author, rating, date)", alias="sortBy"),
    sortOrder: Optional[str] = Query(None, description="Sort order (asc or desc)", alias="sortOrder"),
    offset: Optional[int] = Query(0, ge=0, description="Number of items to skip"),
    limit: Optional[int] = Query(20, gt=0, le=100, description="Number of items to return"),
    db: Session = Depends(get_db)
):
    # Set default values for pagination
    if limit is None:
        limit = 20
    if offset is None:
        offset = 0
        
    # Calculate page number from offset/limit
    page = (offset // limit) + 1
    items_per_page = limit

    # Normalize sort parameters
    normalized_sort_by = sortBy.lower() if sortBy else None
    normalized_sort_order = sortOrder.lower() if sortOrder else 'asc'
    
    # Validate sort parameters
    valid_sort_fields = ['title', 'author', 'rating', 'date', 'publication_date', 'average_rating', 'total_reviews']
    valid_sort_orders = ['asc', 'desc']
    
    if normalized_sort_by and normalized_sort_by not in valid_sort_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by value. Must be one of: {', '.join(valid_sort_fields)}")
    if normalized_sort_order not in valid_sort_orders:
        raise HTTPException(status_code=400, detail=f"Invalid sort_order value. Must be one of: {', '.join(valid_sort_orders)}")
    
    book_service = BookService(db)
    search_params = BookSearchParams(
        search=search,
        sort_by=normalized_sort_by,
        sort_order=normalized_sort_order,
        offset=offset,
        limit=limit,
        page=None,  # We're using offset/limit pagination
        items_per_page=limit  # Using limit as items_per_page for metadata
    )
    
    # Log the parameters for debugging
    logger = logging.getLogger(__name__)
    logger.info(f"Endpoint received: sort_by={normalized_sort_by}, sort_order={normalized_sort_order}")
    books, total_count = book_service.get_books(search_params)
    
    # Calculate pagination metadata
    total_pages = (total_count + items_per_page - 1) // items_per_page if items_per_page else None
    current_page_count = len(books)
    
    return BookListResponse(
        books=books,
        total=total_count,
        page=page,
        items_per_page=items_per_page,
        total_pages=total_pages,
        current_page_count=current_page_count
    )

@router.get("/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book_service = BookService(db)
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    book_service = BookService(db)
    return book_service.create_book(book)

@router.put("/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book: BookUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    book_service = BookService(db)
    updated_book = book_service.update_book(book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    book_service = BookService(db)
    if not book_service.delete_book(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}
