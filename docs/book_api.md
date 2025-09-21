# Book Service API Documentation

## Base URL
```
http://localhost:8000/v1
```

## Authentication
Most endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. List Books
GET `/books`

Retrieve a paginated list of books with optional filtering and sorting.

**Query Parameters:**
- `query` (optional): Search text to filter books by title or author
- `genres` (optional): Array of genre names to filter by (can specify multiple times)
- `sort_by` (optional): Field to sort by - 'title', 'author', 'rating', or 'date'
- `sort_order` (optional): 'asc' or 'desc'
- `page` (optional): Page number (default: 1, min: 1)
- `items_per_page` (optional): Items per page (default: 50, max: 100)

**Example Request:**
```typescript
const response = await axios.get('/v1/books', {
  params: {
    query: 'fantasy',
    genres: ['Fantasy', 'Adventure'],
    sort_by: 'rating',
    sort_order: 'desc',
    page: 1,
    items_per_page: 50
  }
});
```

**Success Response (200 OK):**
```json
{
    "items": [
        {
            "id": 1,
            "title": "The Great Adventure",
            "author": "John Doe",
            "isbn": "1234567890",
            "genres": ["Fantasy", "Adventure"],
            "publication_date": "2025-01-01",
            "average_rating": 4.5,
            "total_reviews": 100
        }
    ],
    "total": 150,
    "page": 1,
    "items_per_page": 50,
    "total_pages": 3
}
```

### 2. Get Single Book
GET `/books/{book_id}`

Retrieve details of a specific book.

**Path Parameters:**
- `book_id`: ID of the book to retrieve

**Example Request:**
```typescript
const response = await axios.get(`/v1/books/${bookId}`);
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "title": "The Great Adventure",
    "author": "John Doe",
    "isbn": "1234567890",
    "genres": ["Fantasy", "Adventure"],
    "publication_date": "2025-01-01",
    "average_rating": 4.5,
    "total_reviews": 100
}
```

### 3. Create Book
POST `/books`

Create a new book. Requires authentication.

**Request Body:**
```json
{
    "title": "New Book Title",
    "author": "Author Name",
    "isbn": "1234567890123",
    "genres": ["Fiction", "Mystery"],
    "publication_date": "2025-09-01"
}
```

**Validation:**
- `title`: Required, 1-255 characters
- `author`: Required, 1-255 characters
- `isbn`: Required, 10-13 characters
- `genres`: Required, non-empty array of strings
- `publication_date`: Optional, valid date format (YYYY-MM-DD)

**Example Request:**
```typescript
const response = await axios.post('/v1/books', bookData, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### 4. Update Book
PUT `/books/{book_id}`

Update an existing book. Requires authentication.

**Path Parameters:**
- `book_id`: ID of the book to update

**Request Body:**
```json
{
    "title": "Updated Title",
    "author": "Updated Author",
    "genres": ["New Genre"],
    "publication_date": "2025-10-01"
}
```

**Validation:**
- All fields are optional
- Same validation rules as Create Book for provided fields

**Example Request:**
```typescript
const response = await axios.put(`/v1/books/${bookId}`, updateData, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### 5. Delete Book
DELETE `/books/{book_id}`

Delete a book. Requires authentication.

**Path Parameters:**
- `book_id`: ID of the book to delete

**Example Request:**
```typescript
const response = await axios.delete(`/v1/books/${bookId}`, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

**Success Response (200 OK):**
```json
{
    "message": "Book deleted successfully"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
    "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
    "detail": "Book not found"
}
```

## TypeScript Interfaces

```typescript
interface Book {
    id: number;
    title: string;
    author: string;
    isbn: string;
    genres: string[];
    publication_date?: string;
    average_rating: number;
    total_reviews: number;
}

interface BookCreate {
    title: string;
    author: string;
    isbn: string;
    genres: string[];
    publication_date?: string;
}

interface BookUpdate {
    title?: string;
    author?: string;
    genres?: string[];
    publication_date?: string;
}

interface BookListResponse {
    items: Book[];
    total: number;
    page: number;
    items_per_page: number;
    total_pages: number;
}
```

## Example Integration (React + Axios)

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/v1';

// Book service class
export class BookService {
  private api;

  constructor(access_token: string) {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Authorization': `Bearer ${access_token}`
      }
    });
  }

  async listBooks(params: {
    query?: string;
    genres?: string[];
    sort_by?: 'title' | 'author' | 'rating' | 'date';
    sort_order?: 'asc' | 'desc';
    page?: number;
    items_per_page?: number;
  }) {
    const response = await this.api.get('/books', { params });
    return response.data as BookListResponse;
  }

  async getBook(id: number) {
    const response = await this.api.get(`/books/${id}`);
    return response.data as Book;
  }

  async createBook(book: BookCreate) {
    const response = await this.api.post('/books', book);
    return response.data as Book;
  }

  async updateBook(id: number, book: BookUpdate) {
    const response = await this.api.put(`/books/${id}`, book);
    return response.data as Book;
  }

  async deleteBook(id: number) {
    await this.api.delete(`/books/${id}`);
  }
}

// Usage example
const bookService = new BookService(access_token);

try {
  // List books with filters
  const books = await bookService.listBooks({
    genres: ['Fantasy'],
    sort_by: 'rating',
    sort_order: 'desc'
  });

  // Get single book
  const book = await bookService.getBook(1);

  // Create new book
  const newBook = await bookService.createBook({
    title: 'New Book',
    author: 'Author Name',
    isbn: '1234567890123',
    genres: ['Fiction']
  });

  // Update book
  await bookService.updateBook(1, {
    title: 'Updated Title'
  });

  // Delete book
  await bookService.deleteBook(1);

} catch (error) {
  if (axios.isAxiosError(error)) {
    console.error('API Error:', error.response?.data?.detail);
  }
}
```

## Best Practices

1. **Error Handling**: Always implement proper error handling for API calls
2. **Token Management**: Store and refresh access tokens appropriately
3. **Loading States**: Show loading indicators during API operations
4. **Validation**: Validate data on the frontend before making API calls
5. **Caching**: Consider implementing client-side caching for frequently accessed books
