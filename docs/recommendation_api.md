# Recommendation Service API Documentation

## Overview
The recommendation service provides personalized book recommendations based on user preferences, reading history, and favorite books. The service includes a fallback mechanism to provide popular book recommendations when personalized recommendations are not available.

## Base URL
```
/recommendations
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Get Recommendations
Returns personalized book recommendations for the authenticated user.

**Endpoint:** `POST /recommendations`

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

**Request Body:**
```typescript
interface RecommendationRequest {
  limit?: number;  // Optional. Number of recommendations to return. Default: 10
}
```

**Response:**
```typescript
interface BookRecommendation {
  book_id: number;
  title: string;
  author: string;
  genres: string[];
  average_rating: number;
  relevance_score: number;
  recommendation_reason: string;
}

interface RecommendationResponse {
  recommendations: BookRecommendation[];
  is_fallback: boolean;  // true if using fallback recommendations
}
```

**Example Request:**
```javascript
const response = await axios.post('/recommendations', 
  { limit: 5 },
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
);
```

**Example Response:**
```json
{
  "recommendations": [
    {
      "book_id": 123,
      "title": "The Great Book",
      "author": "Jane Author",
      "genres": ["Fiction", "Adventure"],
      "average_rating": 4.5,
      "relevance_score": 0.85,
      "recommendation_reason": "Matches your interest in Fiction"
    },
    // ... more recommendations
  ],
  "is_fallback": false
}
```

**Response Status Codes:**
- `200 OK`: Successful request
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Server error

## Integration Example

Here's an example of how to integrate with the recommendation service using React and Axios:

```typescript
import axios from 'axios';

interface BookRecommendation {
  book_id: number;
  title: string;
  author: string;
  genres: string[];
  average_rating: number;
  relevance_score: number;
  recommendation_reason: string;
}

interface RecommendationResponse {
  recommendations: BookRecommendation[];
  is_fallback: boolean;
}

const getRecommendations = async (limit: number = 10): Promise<RecommendationResponse> => {
  try {
    const token = localStorage.getItem('jwt_token'); // Get token from storage
    const response = await axios.post<RecommendationResponse>(
      '/api/recommendations',
      { limit },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // Handle unauthorized error (e.g., redirect to login)
      throw new Error('Please login to get recommendations');
    }
    throw new Error('Failed to fetch recommendations');
  }
};

// Usage in a React component
const RecommendationsComponent: React.FC = () => {
  const [recommendations, setRecommendations] = useState<BookRecommendation[]>([]);
  const [isFallback, setIsFallback] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const result = await getRecommendations(10);
        setRecommendations(result.recommendations);
        setIsFallback(result.is_fallback);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
    };

    fetchRecommendations();
  }, []);

  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Recommended Books</h2>
      {isFallback && (
        <p>Showing popular books based on overall ratings</p>
      )}
      <div className="recommendations-list">
        {recommendations.map(book => (
          <div key={book.book_id} className="book-card">
            <h3>{book.title}</h3>
            <p>By: {book.author}</p>
            <p>Rating: {book.average_rating}</p>
            <p>{book.recommendation_reason}</p>
            <div className="genres">
              {book.genres.map(genre => (
                <span key={genre} className="genre-tag">{genre}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Error Handling
The service returns standard HTTP status codes and JSON error responses:

```typescript
interface ErrorResponse {
  detail: string;
}
```

Common error scenarios:
1. Missing/invalid token: 401 Unauthorized
2. Server error: 500 Internal Server Error with error details

## Notes
- The service automatically falls back to popular book recommendations if:
  - The user has no reading history or preferences
  - An error occurs in the recommendation algorithm
  - The user is new to the platform
- The `relevance_score` indicates how well the recommendation matches the user's preferences
- Recommendations exclude books that the user has already reviewed or marked as favorites
- The service is optimized for response times under 2 seconds
