from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session
from app.db.models import User, InvalidatedToken
from app.core.auth import get_password_hash, create_access_token
from datetime import datetime, UTC, timedelta

def test_logout(client: TestClient, db: Session):
    """Test /auth/logout endpoint."""
    # First register and login a user to get a token
    unique_email = "test_logout@example.com"
    password = "testpassword123"
    
    # Register
    register_response = client.post(
        "/v1/auth/register",
        data={"name": "Test User", "username": unique_email, "password": password}
    )
    assert register_response.status_code == 200
    
    # Login
    login_response = client.post(
        "/v1/auth/login",
        data={"username": unique_email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Try logout
    logout_response = client.post(
        "/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_response.status_code == 200
    assert "Successfully logged out" in logout_response.json()["message"]
    
    # Verify token is invalidated
    invalidated = db.query(InvalidatedToken).filter(InvalidatedToken.token == token).first()
    assert invalidated is not None
    
    # Try to use invalidated token
    me_response = client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 401
