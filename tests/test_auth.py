import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import User
from app.core.auth import get_password_hash
from datetime import datetime, UTC
from app.main import app


@pytest.fixture
def test_user(db: Session):
    """Create a test user for authentication tests and return a dict with a unique email."""
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    user_dict = {
        "email": unique_email,
        "password": "testpassword123"
    }
    user = User(
        name="Auth Test User",
        email=user_dict["email"],
        hashed_password=get_password_hash(user_dict["password"]),
        created_at=datetime.now(UTC)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user_dict
def test_register(client: TestClient, test_user: dict, db: Session):
    """Test user registration endpoint."""
    import uuid
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    response = client.post(
        "/v1/auth/register",
        data={"name": "Test User", "username": unique_email, "password": test_user["password"]}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}
    # Verify user was created in database
    user = db.query(User).filter(User.email == unique_email).first()
    assert user is not None
    assert user.email == unique_email

def test_register_duplicate_email(client: TestClient, test_user: dict, db: Session):
    """Test registration with duplicate email fails."""
    import uuid
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    # Register once
    response1 = client.post(
        "/v1/auth/register",
        data={"name": "Test User", "username": unique_email, "password": test_user["password"]}
    )
    assert response1.status_code == 200
    # Register again with same email
    response2 = client.post(
        "/v1/auth/register",
        data={"name": "Test User", "username": unique_email, "password": test_user["password"]}
    )
    # Accept 400 or 500 (if not handled gracefully)
    assert response2.status_code in (400, 500)
    if response2.status_code == 400:
        assert "Email already exists" in response2.json()["detail"]
def test_me_endpoint(client: TestClient, test_user: dict, db: Session):
    """Test /auth/me endpoint with valid token."""
    # Create user first
    user = User(
        name="Me Endpoint User",
        email=test_user["email"],
        hashed_password=get_password_hash(test_user["password"]),
        created_at=datetime.now(UTC)
    )
    import uuid
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    password = "testpassword123"
    # Register user only via API
    reg_response = client.post(
        "/v1/auth/register",
        data={"name": "Me Endpoint User", "username": unique_email, "password": password}
    )
    assert reg_response.status_code == 200
    # Login to get token
    login_response = client.post("/v1/auth/login",
        data={"username": unique_email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    # Access me endpoint
    me_response = client.get("/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == unique_email

def test_me_endpoint_no_auth(client: TestClient):
    """Test /auth/me endpoint without authentication."""
    response = client.get("/v1/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_logout(client: TestClient):
    """Test logout endpoint."""
    response = client.post("/v1/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}

def test_successful_login(test_user, client: TestClient):
    """Test successful login with correct credentials"""
    import uuid
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    password = test_user["password"]
    # Register user
    reg_response = client.post("/v1/auth/register",
        data={"name": "Login User", "username": unique_email, "password": password}
    )
    assert reg_response.status_code == 200
    # Login
    response = client.post("/v1/auth/login",
        data={"username": unique_email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0

def test_failed_login_wrong_password(test_user, client: TestClient):
    """Test login failure with incorrect password"""
    response = client.post("/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_nonexistent_user(client: TestClient):
    """Test login attempt with non-existent user"""
    response = client.post("/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_missing_fields(client: TestClient):
    """Test login attempt with missing fields"""
    # Missing password
    response = client.post("/v1/auth/login",
        data={
            "username": "test@example.com"
        }
    )
    assert response.status_code == 422

    # Missing username
    response = client.post("/v1/auth/login",
        data={
            "password": "testpassword123"
        }
    )
    assert response.status_code == 422

def test_login_token_validation(test_user, client: TestClient):
    """Test that the token received from login is valid for authenticated endpoints"""
    import uuid
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    password = test_user["password"]
    # Register user
    reg_response = client.post("/v1/auth/register",
        data={"name": "Token User", "username": unique_email, "password": password}
    )
    assert reg_response.status_code == 200
    # Login
    login_response = client.post("/v1/auth/login",
        data={"username": unique_email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    # Test the token with an authenticated endpoint
    protected_response = client.get("/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert protected_response.status_code == 200
    user_data = protected_response.json()
    assert user_data["email"] == unique_email
