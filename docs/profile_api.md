# Profile Service API Documentation

## Base URL
```
http://localhost:8000/v1
```

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Get My Profile
GET `/profile/me`

Retrieve the current user's profile information, including their reviews and favorites.

**Example Request:**
```typescript
const response = await axios.get('/v1/profile/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "profile_image_url": "http://localhost:8000/storage/profiles/image.jpg",
    "created_at": "2025-09-01T10:00:00Z",
    "last_login": "2025-09-01T15:00:00Z",
    "reviews": [
        {
            "id": 1,
            "book_id": 123,
            "content": "Great book!",
            "rating": 5,
            "created_at": "2025-09-01T10:00:00Z",
            "updated_at": null
        }
    ],
    "favorites": [
        {
            "id": 1,
            "book_id": 456,
            "created_at": "2025-09-01T10:00:00Z"
        }
    ]
}
```

### 2. Update My Profile
PUT `/profile/me`

Update the current user's profile information.

**Request Body:**
```json
{
    "email": "newemail@example.com",
    "profile_image_url": "http://localhost:8000/storage/profiles/new-image.jpg"
}
```

**Example Request:**
```typescript
const response = await axios.put('/v1/profile/me', profileData, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

**Success Response (200 OK):**
Same as Get Profile response

### 3. Get My Reviews
GET `/profile/me/reviews`

Retrieve a paginated list of the current user's reviews.

**Query Parameters:**
- `limit` (optional): Number of reviews to return (default: 10)
- `offset` (optional): Number of reviews to skip (default: 0)

**Example Request:**
```typescript
const response = await axios.get('/v1/profile/me/reviews', {
  params: {
    limit: 10,
    offset: 0
  },
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

**Success Response (200 OK):**
```json
[
    {
        "id": 1,
        "book_id": 123,
        "content": "Great book!",
        "rating": 5,
        "created_at": "2025-09-01T10:00:00Z",
        "updated_at": null
    }
]
```

### 4. Get My Favorites
GET `/profile/me/favorites`

Retrieve a paginated list of the current user's favorite books.

**Query Parameters:**
- `limit` (optional): Number of favorites to return (default: 10)
- `offset` (optional): Number of favorites to skip (default: 0)

**Example Request:**
```typescript
const response = await axios.get('/v1/profile/me/favorites', {
  params: {
    limit: 10,
    offset: 0
  },
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

**Success Response (200 OK):**
```json
[
    {
        "id": 1,
        "book_id": 456,
        "created_at": "2025-09-01T10:00:00Z"
    }
]
```

### 5. Add to Favorites
POST `/profile/me/favorites/{book_id}`

Add a book to the current user's favorites.

**Path Parameters:**
- `book_id`: ID of the book to add to favorites

**Example Request:**
```typescript
const response = await axios.post(`/v1/profile/me/favorites/${bookId}`, null, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "book_id": 456,
    "created_at": "2025-09-01T10:00:00Z"
}
```

### 6. Remove from Favorites
DELETE `/profile/me/favorites/{book_id}`

Remove a book from the current user's favorites.

**Path Parameters:**
- `book_id`: ID of the book to remove from favorites

**Example Request:**
```typescript
await axios.delete(`/v1/profile/me/favorites/${bookId}`, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

**Success Response (204 No Content)**

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
    "detail": "Profile not found"
}
```

## TypeScript Interfaces

```typescript
interface Profile {
    id: number;
    email: string;
    name: string;
    profile_image_url?: string;
    created_at: string;
    last_login?: string;
    reviews: ReviewBrief[];
    favorites: Favorite[];
}

interface ProfileUpdate {
    email?: string;
    profile_image_url?: string;
}

interface ReviewBrief {
    id: number;
    book_id: number;
    content: string;
    rating: number;
    created_at: string;
    updated_at?: string;
}

interface Favorite {
    id: number;
    book_id: number;
    created_at: string;
}

```

## Example Integration (React + Axios)

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/v1';

export class ProfileService {
  private api;

  constructor(access_token: string) {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Authorization': `Bearer ${access_token}`
      }
    });
  }

  async getProfile() {
    const response = await this.api.get('/profile/me');
    return response.data as Profile;
  }

  async updateProfile(data: ProfileUpdate) {
    const response = await this.api.put('/profile/me', data);
    return response.data as Profile;
  }

  async getReviews(limit: number = 10, offset: number = 0) {
    const response = await this.api.get('/profile/me/reviews', {
      params: { limit, offset }
    });
    return response.data as ReviewBrief[];
  }

  async getFavorites(limit: number = 10, offset: number = 0) {
    const response = await this.api.get('/profile/me/favorites', {
      params: { limit, offset }
    });
    return response.data as Favorite[];
  }

  async addToFavorites(bookId: number) {
    const response = await this.api.post(`/profile/me/favorites/${bookId}`);
    return response.data as Favorite;
  }

  async removeFromFavorites(bookId: number) {
    await this.api.delete(`/profile/me/favorites/${bookId}`);
  }
}

// Usage example
const profileService = new ProfileService(access_token);

try {
  // Get user profile
  const profile = await profileService.getProfile();

  // Update profile
  await profileService.updateProfile({
    profile_image_url: 'http://example.com/image.jpg'
  });

  // Get user's reviews
  const reviews = await profileService.getReviews(10, 0);

  // Manage favorites
  const favorites = await profileService.getFavorites();
  await profileService.addToFavorites(123);
  await profileService.removeFromFavorites(456);

} catch (error) {
  if (axios.isAxiosError(error)) {
    console.error('API Error:', error.response?.data?.detail);
  }
}
```

## Best Practices

1. **Authentication**: Always handle token expiration and refresh flows
2. **Error Handling**: Implement proper error handling for all API calls
3. **Loading States**: Show loading indicators during API operations
4. **Pagination**: Implement proper pagination for reviews and favorites lists
5. **Caching**: Consider caching profile data for better performance
6. **Image Upload**: Handle profile image upload through the Storage Service API
