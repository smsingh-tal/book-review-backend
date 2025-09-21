from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=10, max_length=13)
    genres: List[str] = Field(..., min_length=1)
    publication_date: Optional[date] = None
    
class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    genres: Optional[List[str]] = Field(None, min_length=1)
    publication_date: Optional[date] = None

from pydantic import ConfigDict

class Book(BookBase):
    id: int
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    total_reviews: int = Field(default=0, ge=0)
    
    model_config = ConfigDict(from_attributes=True)  # Modern way to configure Pydantic models

class BookListResponse(BaseModel):
    books: List[Book]
    total: int
    page: Optional[int] = None
    items_per_page: Optional[int] = None
    total_pages: Optional[int] = None
    current_page_count: Optional[int] = None  # Number of items on the current page

    model_config = ConfigDict(from_attributes=True)

class BookSearchParams(BaseModel):
    search: Optional[str] = None
    sort_by: Optional[str] = Field(None, description="Field to sort by (title, author, rating, date)")
    sort_order: Optional[str] = Field(None, description="Sort order (asc or desc)")
    offset: Optional[int] = Field(default=None, ge=0)
    limit: Optional[int] = Field(default=None, gt=0, le=100)
    page: Optional[int] = Field(default=None, gt=0)
    items_per_page: Optional[int] = Field(default=None, gt=0, le=100)
    
    @property
    def valid_sort_fields(self):
        return ['title', 'author', 'rating', 'average_rating', 'total_reviews', 'date', 'publication_date']
    
    @property
    def valid_sort_orders(self):
        return ['asc', 'desc']
    
    def validate_sort_params(self):
        if self.sort_by and self.sort_by not in self.valid_sort_fields:
            raise ValueError(f"Invalid sort_by value. Must be one of: {', '.join(self.valid_sort_fields)}")
        if self.sort_order and self.sort_order.lower() not in self.valid_sort_orders:
            raise ValueError(f"Invalid sort_order value. Must be one of: {', '.join(self.valid_sort_orders)}")
