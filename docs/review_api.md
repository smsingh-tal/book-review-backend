# Review Service API Documentation

## Base URL
```
http://localhost:8000/v1
```

## Authentication
All endpoints except for GET /reviews (listing reviews) require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. List Reviews
GET `/reviews`

Retrieve a list of reviews with optional filtering and sorting.

**Query Parameters:**
- `book_id` (optional): Filter reviews by book ID
- `user_id` (optional): Filter reviews by user ID
- `rating` (optional): Filter by rating (1-5)
- `sort_by` (optional): Sort field - 'date', 'rating', or 'votes'
- `sort_order` (optional): 'asc' or 'desc'
- `page` (optional): Page number (default: 1)
- `items_per_page` (optional): Items per page (default: 50, max: 100)

**Response:**
```json
{
    "items": [
        {
            "id": 1,
            "content": "Great book!",
            "rating": 5,
            "user_id": 123,
            "book_id": 456,
            "created_at": "2025-09-01T10:00:00Z",
            "updated_at": null,
            "helpful_votes": 10,
            "unhelpful_votes": 2,
            "user": {
                "id": 123,
                "email": "user@example.com"
            },
            "can_edit": true
        }
    ],
    "total": 100,
    "page": 1,
    "items_per_page": 50,
    "total_pages": 2
}
```

### 2. Get Single Review
GET `/reviews/{review_id}`

Retrieve a single review by ID.

**Response:**
```json
{
    "id": 1,
    "content": "Great book!",
    "rating": 5,
    "user_id": 123,
    "book_id": 456,
    "created_at": "2025-09-01T10:00:00Z",
    "updated_at": null,
    "helpful_votes": 10,
    "unhelpful_votes": 2,
    "user": {
        "id": 123,
        "email": "user@example.com"
    },
    "can_edit": true
}
```

### 3. Create Review
POST `/reviews`

Create a new review for a book. Users can only create one review per book.

**Request Body:**
```json
{
    "book_id": 456,
    "content": "This is my review",
    "rating": 5
}
```

**Validation:**
- `content`: Minimum 5 characters
- `rating`: Integer between 1 and 5
- Cannot review the same book twice

**Response:**
Same as Get Single Review response

### 4. Update Review
PUT `/reviews/{review_id}`

Update an existing review. Only available within 24 hours of creation.

**Request Body:**
```json
{
    "content": "Updated review content",
    "rating": 4
}
```

**Validation:**
- `content`: Minimum 5 characters if provided
- `rating`: Integer between 1 and 5 if provided
- Must be within 24 hours of creation
- Can only update own reviews

### 5. Delete Review
DELETE `/reviews/{review_id}`

Soft delete a review. Only the owner can delete their review.

**Response:**
```json
{
    "message": "Review deleted successfully"
}
```

### 6. Vote on Review
POST `/reviews/{review_id}/vote`

Mark a review as helpful or unhelpful.

**Request Body:**
```json
{
    "is_helpful": true
}
```

**Validation:**
- Cannot vote on own review
- Can change vote from helpful to unhelpful or vice versa

**Response:**
```json
{
    "message": "Vote recorded successfully"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Error message describing the validation failure"
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
    "detail": "Review not found"
}
```

## Integration Examples

### TypeScript Interfaces
```typescript
interface Review {
    id: number;
    content: string;
    rating: number;
    user_id: number;
    book_id: number;
    created_at: string;
    updated_at: string | null;
    helpful_votes: number;
    unhelpful_votes: number;
    user: {
        id: number;
        email: string;
    };
    can_edit: boolean;
}

interface CreateReviewRequest {
    book_id: number;
    content: string;
    rating: number;
}

interface UpdateReviewRequest {
    content?: string;
    rating?: number;
}

interface ReviewsResponse {
    items: Review[];
    total: number;
    page: number;
    items_per_page: number;
    total_pages: number;
}
```

### Axios Example
```typescript
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/v1',
    headers: {
        'Content-Type': 'application/json',
    }
});

// Set auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// List reviews for a book
const getBookReviews = async (bookId: number, page = 1) => {
    const response = await api.get<ReviewsResponse>('/reviews', {
        params: {
            book_id: bookId,
            page,
            sort_by: 'date',
            sort_order: 'desc'
        }
    });
    return response.data;
};

// Create a review
const createReview = async (review: CreateReviewRequest) => {
    const response = await api.post<Review>('/reviews', review);
    return response.data;
};

// Update a review
const updateReview = async (reviewId: number, review: UpdateReviewRequest) => {
    const response = await api.put<Review>(`/reviews/${reviewId}`, review);
    return response.data;
};

// Vote on a review
const voteOnReview = async (reviewId: number, isHelpful: boolean) => {
    const response = await api.post(`/reviews/${reviewId}/vote`, {
        is_helpful: isHelpful
    });
    return response.data;
};
```

## Important Notes
1. All timestamps are in UTC format
2. Reviews can only be edited within 24 hours of creation
3. The `can_edit` field in the review response indicates if the review is still editable
4. Users can change their votes on a review
5. Rating updates automatically update the book's average rating
6. Review deletion is soft delete - the review will no longer appear in listings
7. Pagination is 1-based (first page is 1, not 0)

## Rate Limits
- 100 requests per minute per IP
- 5 review creations per book per minute per user
- 10 votes per minute per user
