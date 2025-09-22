# Recommendation Service API Documentation

## Overview
The recommendation service provides personalized book recommendations using multiple strategies:
1. Top-rated books based on user preferences and rating patterns
2. Similar books based on user's favorite genres and reading history
3. AI-powered recommendations using OpenAI's GPT model

The service includes intelligent fallback mechanisms and caching for optimal performance.

## Base URL
```
/v1/recommendations
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Get Recommendations
Returns personalized book recommendations for the authenticated user using the specified recommendation strategy.

**Endpoint:** `POST /v1/recommendations`

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

**Request Body:**
```typescript
interface RecommendationRequest {
  limit?: number;              // Optional. Number of recommendations (1-50). Default: 10
  recommendation_type: string; // Required. One of: "top_rated", "similar", "ai"
  genre?: string;             // Optional. Filter recommendations by specific genre
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
  rating_count: number;
  publication_year?: number;
  relevance_score: number;
  recommendation_reason: string;
}

interface RecommendationResponse {
  recommendations: BookRecommendation[];
  is_fallback: boolean;           // true if using fallback recommendations
  fallback_reason?: string;       // explanation if fallback was used
  recommendation_type: string;    // the type of recommendations returned
}
```

**Recommendation Types:**

1. **top_rated** (Default)
   - Returns highest-rated books matching user's rating patterns
   - Considers user's average rating threshold
   - Excludes books with too few ratings
   - Filters out already read/reviewed books

2. **similar**
   - Returns books similar to user's favorites
   - Uses genre matching and preference scoring
   - Considers user's reading history
   - Provides detailed matching explanations

3. **ai**
   - Uses OpenAI to generate personalized recommendations
   - Considers user's reading history and preferences
   - Falls back to "similar" if AI is unavailable
   - Includes cache mechanism for performance

**Example Requests:**
```javascript
// Get top-rated recommendations
const topRatedResponse = await axios.post('/v1/recommendations', 
  {
    limit: 5,
    recommendation_type: 'top_rated'
  },
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
);

// Get genre-specific similar books
const similarResponse = await axios.post('/v1/recommendations', 
  {
    limit: 10,
    recommendation_type: 'similar',
    genre: 'Mystery'
  },
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
);

// Get AI-powered recommendations
const aiResponse = await axios.post('/v1/recommendations', 
  {
    limit: 5,
    recommendation_type: 'ai'
  },
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
      "title": "The Great Mystery",
      "author": "Jane Author",
      "genres": ["Mystery", "Thriller"],
      "average_rating": 4.5,
      "rating_count": 128,
      "publication_year": 2024,
      "relevance_score": 0.85,
      "recommendation_reason": "Highly rated mystery novel matching your reading preferences"
    }
  ],
  "is_fallback": false,
  "recommendation_type": "top_rated"
}
```

**Response Status Codes:**
- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Server error

**Error Responses:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Performance Considerations
- Response time: < 2 seconds for non-AI recommendations
- Response time: < 5 seconds for AI recommendations
- Cache duration: 24 hours for AI recommendations
- Rate limits: 100 requests per minute per user
- Minimum rating count: 5 reviews per book for top-rated recommendations

## Notes
- The service automatically excludes books that the user has already read or reviewed
- The `relevance_score` ranges from 0 to 1, indicating how well the recommendation matches the user's preferences
- When using genre filters, the service will still return cross-genre recommendations if they are highly relevant
- The AI recommendation type requires OpenAI API configuration on the server
- Fallback mechanisms ensure users always get recommendations, even if their preferred method fails

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
