# Book Review Platform - Technical PRD

## 1. Technical Architecture Overview

### 1.1 Technology Stack
#### Frontend
- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit or React Query
- **UI Components**: Material-UI (MUI) or Chakra UI
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Testing**: Jest + React Testing Library

#### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Migration Tool**: Alembic
- **Authentication**: PyJWT + python-jose
- **Password Hashing**: Passlib + bcrypt
- **Validation**: Pydantic
- **Testing**: pytest
- **ASGI Server**: uvicorn

#### Database
- **RDBMS**: PostgreSQL 15+
- **Features Used**:
  - Full-text search
  - Array data type (for genres)
  - JSON/JSONB support
  - Advanced indexing

#### Storage
- **Service**: AWS S3 or MinIO (local development)
- **SDK**: boto3

#### Development Tools
- **Package Management**: 
  - Frontend: npm/yarn
  - Backend: Poetry
- **Code Quality**: 
  - Frontend: ESLint + Prettier
  - Backend: Black
- **Containerization**: Docker + docker-compose
- **Version Control**: Git

#### CI/CD & Monitoring
- **CI/CD**: GitHub Actions or GitLab CI
- **Metrics**: Prometheus + Grafana
- **Error Tracking**: Sentry
- **Logging**: ELK Stack

### 1.2 System Components
- **Frontend**: Single Page Application (Mobile-responsive)
- **Backend**: RESTful API Services
- **Database**: PostgreSQL (Relational)
- **Storage**: S3-compatible Storage System
- **AI Integration**: OpenAI GPT-3.5 API

### 1.2 High-Level Architecture
```
[Client Tier]
Mobile/Web Clients
        ↓
[API Gateway]
REST APIs (Versioned)
        ↓
[Application Tier]
Authentication Service
Book Management Service
Review Service
User Profile Service
Recommendation Service
        ↓
[Data Tier]
SQL Database
File Storage
```

## 2. Technical Requirements

### TR-001: Authentication System (Maps to 001_AUTH)
**Core Requirements:**
- JWT-based authentication
- 30-minute inactivity timeout
- No social login integration (future scope)
- Password validation (8+ characters, 1 numeric, 1 special character)

**Technical Specifications:**
- JWT access tokens with short expiry (30 minutes)
- Token-based session management
- Secure password hashing using bcrypt
- HTTPS enforcement for all API endpoints

### TR-002: Database Design (Maps to multiple BRDs)
**Core Requirements:**
- SQL Database implementation
- Optimized indexing for 2-second search requirement
- Support for 500-1000 initial users with 50% YoY growth

**Key Tables:**
1. Users
2. Books
3. Reviews
4. Ratings
5. UserFavorites
6. ReviewVotes

**Indexing Strategy:**
- Composite indexes on books (title, author)
- Indexes on genre combinations
- Indexes on review timestamps
- Indexes on user activity metrics

### TR-003: API Design
**Core Requirements:**
- RESTful architecture
- URL-based versioning (/v1/*)
- JSON response format
- Standardized error handling

**API Groups:**
1. Authentication APIs
2. Book Management APIs
3. Review Management APIs
4. User Profile APIs
5. Recommendation APIs

### TR-004: Search Implementation (Maps to 002_BOOK)
**Core Requirements:**
- Database-level search implementation
- Maximum 2-second response time
- Support for multiple filter combinations

**Technical Specifications:**
- SQL LIKE queries with indexes
- Paginated responses (50 items per page)
- Sorted results by multiple criteria
- Filter chain implementation

### TR-005: Review System (Maps to 003_REV)
**Core Requirements:**
- Soft delete implementation
- 24-hour edit window
- Rating aggregation system

**Technical Specifications:**
- Timestamp-based edit validation
- Normalized rating storage
- Helpful/unhelpful voting system
- Review state management

### TR-006: File Storage (Maps to 004_PROF)
**Core Requirements:**
- Direct file storage system
- Support for profile pictures
- Support for book cover images

**Technical Specifications:**
- Maximum file size: 5MB
- Supported formats: JPG, PNG
- File naming convention: UUID-based
- Basic image optimization

### TR-007: Recommendation System (Maps to 005_REC)
**Core Requirements:**
- Synchronous GPT-3.5 integration
- 15-second maximum latency
- Fallback recommendation system

**Technical Specifications:**
- GPT-3.5 API integration
- Timeout handling
- Generic recommendations fallback
- User history-based filtering

### TR-008: Performance Requirements (Maps to 006_TECH)
**Core Requirements:**
- < 2 second response time for searches
- 99.9% system availability
- Mobile-responsive design

**Technical Specifications:**
- Database query optimization
- Error rate monitoring
- Response time tracking
- Load handling capacity

## 3. System Architecture Details

### 3.1 Database Schema
```sql
-- Core tables (simplified)
Users (
    id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    profile_image_url VARCHAR(255)
)

Books (
    id BIGINT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genres TEXT[] NOT NULL,
    publication_date DATE,
    average_rating DECIMAL(3,2) DEFAULT 0.0,
    total_reviews INT DEFAULT 0
)

Reviews (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES Users(id),
    book_id BIGINT REFERENCES Books(id),
    content TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    UNIQUE(user_id, book_id)
)
```

### 3.2 API Endpoints Structure
```
/v1/auth
  POST /register          # Create new user account
  POST /login            # Authenticate user
  POST /logout           # Invalidate session
  
/v1/books
  GET /                  # List books (with filters)
  GET /{id}             # Get book details
  GET /search           # Search books
  
/v1/reviews
  POST /                # Create review
  PUT /{id}            # Update review
  DELETE /{id}         # Soft delete review
  
/v1/recommendations
  GET /                # Get personalized recommendations
```

### 3.3 Security Measures
1. JWT Authentication
   - Access token expiry: 30 minutes
   - HTTPS only cookies
   - XSS protection headers

2. Input Validation
   - Request payload validation
   - File upload validation
   - SQL injection prevention

3. Error Handling
   - Sanitized error messages
   - Proper error logging
   - No sensitive data in responses

## 4. Development Guidelines

### 4.1 Code Organization

#### Frontend Structure
```
src/
  ├── components/      # Reusable UI components
  ├── features/        # Feature-based modules
  ├── hooks/          # Custom React hooks
  ├── layouts/        # Page layouts
  ├── services/       # API service interfaces
  ├── store/          # Redux store configuration
  ├── types/          # TypeScript type definitions
  ├── utils/          # Utility functions
  └── App.tsx         # Root component
```

#### Backend Structure
```
app/
  ├── api/            # API routes and endpoints
  ├── core/           # Core functionality
  │   ├── config.py   # Configuration management
  │   └── security.py # Security utilities
  ├── db/            # Database
  │   ├── models.py   # SQLAlchemy models
  │   └── session.py  # Database session
  ├── schemas/        # Pydantic schemas
  ├── services/       # Business logic
  ├── utils/          # Utility functions
  └── main.py        # Application entry point
```

- Feature-based module organization
- Clear separation of concerns
- Service layer architecture
- Repository pattern for data access

### 4.2 Error Handling
- Standardized error responses
- Proper error logging
- User-friendly error messages
- Error tracking capability

### 4.3 Testing Requirements
- Unit test coverage > 80%
- Integration tests for critical paths
- Performance testing for search functionality
- Load testing for concurrent users

## 5. Monitoring and Metrics

### 5.1 Key Metrics
- API response times
- Error rates
- System availability
- Database query performance

### 5.2 Logging Requirements
- API access logs
- Error logs
- Performance metrics
- User activity logs

## 6. Deployment Strategy

### 6.1 Infrastructure
- Single region deployment
- Medium-sized server configuration
- Vertical scaling approach
- Regular backup system

### 6.2 Release Process
- Feature-based releases
- Automated deployment pipeline
- Rollback capability
- Zero-downtime updates

## 7. Future Considerations

### 7.1 Scalability
- Potential migration to microservices
- Caching implementation
- CDN integration
- Database sharding

### 7.2 Feature Extensions
- Social login integration
- Advanced search capabilities
- Real-time notifications
- Mobile applications

## 8. Dependencies

### 8.1 External Services
- OpenAI GPT-3.5 API
- Email Service (for notifications)

### 8.2 Third-party Libraries
- JWT Authentication library
- SQL ORM
- API validation library
- File upload handling
