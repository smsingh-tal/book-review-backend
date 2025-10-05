# Authentication API Documentation

## Base URL
```
http://localhost:8000
```

## Available Endpoints

### 1. User Registration
Register a new user account and automatically receive an access token.

**Endpoint:** `POST /auth/register`

**Content-Type:** `application/x-www-form-urlencoded`


**Request Body Parameters:**
```
name: string (required)
username: string (email address, required, must be unique)
password: string (min 8 characters, required)
```


**Example Request:**
```typescript
// Using form data
const response = await axios.post('/auth/register', 
  new URLSearchParams({
    name: 'John Doe',
    username: 'user@example.com',
    password: 'yourpassword123'
  }), 
  {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }
);

// Or using JSON
const jsonResponse = await axios.post('/auth/register/json', 
  {
    name: 'John Doe',
    username: 'user@example.com',
    password: 'yourpassword123'
  }, 
  {
    headers: {
      'Content-Type': 'application/json'
    }
  }
);
```


**Success Response (200 OK):**
```json
{
  "message": "User created successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```


**Error Responses:**
- `400 Bad Request`: Email already exists
- `400 Bad Request`: Provide name, username and password as JSON or form data
- `500 Internal Server Error`: Error creating user

### 2. User Login
Authenticate a user and receive an access token.

**Endpoint:** `POST /auth/login`

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body Parameters:**
```
username: string (email address)
password: string
```

**Example Request:**
```typescript
const response = await axios.post('/auth/login', 
  new URLSearchParams({
    username: 'user@example.com',
    password: 'yourpassword123'
  }), 
  {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }
);
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect email or password

### 3. Get Current User
Get information about the currently authenticated user.

**Endpoint:** `GET /auth/me`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Example Request:**
```typescript
const response = await axios.get('/auth/me', {
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
  "created_at": "2025-08-31T10:00:00.000Z",
  "status": "active"
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated or invalid token

### 4. Logout
Invalidate the current session.

**Endpoint:** `POST /auth/logout`

**Example Request:**
```typescript
const response = await axios.post('/auth/logout');
```

**Success Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

## Authentication Flow


1. **Registration:**
  - Call the registration endpoint with name, email (username), and password
  - Email must be unique; duplicate emails will return a 400 error with message "Email already exists"
  - Handle the success/error response appropriately

2. **Login:**
   - Call the login endpoint with credentials
   - On success, store the returned access token securely (e.g., in memory for SPA)
   - Include the token in subsequent authenticated requests

3. **Making Authenticated Requests:**
   - Include the access token in the Authorization header
   - Handle 401 responses by redirecting to login

4. **Logout:**
   - Call the logout endpoint
   - Remove the stored access token
   - Redirect to login page

## Example Frontend Implementation

Here's a basic example using axios interceptors to handle authentication:

```typescript
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth service example
export const authService = {
  async register(email: string, password: string) {
    const response = await api.post('/auth/register', 
      new URLSearchParams({ username: email, password }), 
      {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      }
    );
    return response.data;
  },

  async login(email: string, password: string) {
    const response = await api.post('/auth/login', 
      new URLSearchParams({ username: email, password }), 
      {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      }
    );
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async logout() {
    await api.post('/auth/logout');
    localStorage.removeItem('access_token');
  }
};
```

## Security Considerations

1. **Token Storage:**
   - Store the access token in memory for SPAs
   - Don't store sensitive data in localStorage
   - Consider using HTTP-only cookies for enhanced security

2. **Token Expiration:**
   - Access tokens expire after 30 minutes
   - Handle token expiration by redirecting to login

3. **CORS:**
   - The API allows cross-origin requests
   - Ensure your frontend domain is properly configured

4. **Password Requirements:**
   - Minimum 8 characters
   - At least one numeric character
   - At least one special character

## Error Handling

The API returns error responses in the following format:

```json
{
  "detail": "Error message here"
}
```


Common error scenarios to handle:
1. Registration with existing email (returns 400 with "Email already exists")
2. Registration missing required fields (returns 400)
3. Login with incorrect credentials
4. Accessing protected routes without authentication
5. Token expiration
6. Network errors

## Development Setup

1. **Environment Configuration:**
   ```typescript
   // config.ts
   export const config = {
     apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000'
   };
   ```

2. **Start the Backend Server:**
   ```bash
   cd book-review-backend
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the API:**
   ```bash
   # Using curl
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=test@example.com&password=testpass123"
   ```
