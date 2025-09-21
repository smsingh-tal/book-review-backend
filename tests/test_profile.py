import pytest
from datetime import datetime, timezone
from app.services.profile import ProfileService
from app.schemas.profile import ProfileUpdate
from app.db.models import User, Book, Review, UserFavorite

@pytest.fixture
def test_user(db):
    user = User(
        name="Profile User",
        email="test@example.com",
        hashed_password="dummy_hash",
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def test_book(db):
    book = Book(
        title="Test Book",
        author="Test Author",
        genres=["test_genre"],
        publication_date=datetime.now(timezone.utc).date(),
        isbn="1234567890123"  # 13 digit ISBN
    )
    db.add(book)
    db.commit()
    return book

def test_get_user_profile(db, test_user):
    profile_service = ProfileService(db)
    profile = profile_service.get_user_profile(test_user.id)
    assert profile is not None
    assert profile.id == test_user.id
    assert profile.email == test_user.email
    assert profile.name == "Profile User"

def test_update_profile(db, test_user):
    profile_service = ProfileService(db)
    update_data = ProfileUpdate(
        email="updated@example.com",
        name="Updated Name",
        profile_image_url="https://example.com/image.jpg"
    )
    
    updated_profile = profile_service.update_profile(test_user.id, update_data)
    assert updated_profile.email == "updated@example.com"
    assert updated_profile.name == "Updated Name"
    assert updated_profile.profile_image_url == "https://example.com/image.jpg"

def test_update_profile_nonexistent_user(db):
    profile_service = ProfileService(db)
    update_data = ProfileUpdate(
        email="test@example.com",
        name="Test User"
    )
    
    with pytest.raises(ValueError):
        profile_service.update_profile(999, update_data)

def test_get_user_reviews(db, test_user):
    # Create test books
    books = []
    for i in range(3):
        book = Book(
            title=f"Test Book {i}",
            author=f"Test Author {i}",
            genres=["test_genre"],
            publication_date=datetime.now(timezone.utc).date(),
            isbn=f"123456789{i:04}"  # 13 digit ISBN
        )
        db.add(book)
        books.append(book)
    db.commit()

    # Create reviews for each book
    reviews = []
    for i, book in enumerate(books):
        review = Review(
            user_id=test_user.id,
            book_id=book.id,
            text=f"Test review {i}",
            rating=4,
            created_at=datetime.now(timezone.utc)
        )
        db.add(review)
        reviews.append(review)
    db.commit()

    profile_service = ProfileService(db)
    user_reviews = profile_service.get_user_reviews(test_user.id)
    
    assert len(user_reviews) == 3
    assert all(r.user_id == test_user.id for r in user_reviews)

def test_get_user_favorites(db, test_user, test_book):
    # Create test favorites
    favorite = UserFavorite(
        user_id=test_user.id,
        book_id=test_book.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(favorite)
    db.commit()

    profile_service = ProfileService(db)
    favorites = profile_service.get_user_favorites(test_user.id)
    
    assert len(favorites) == 1
    assert favorites[0].user_id == test_user.id
    assert favorites[0].book_id == test_book.id

def test_add_favorite(db, test_user, test_book):
    profile_service = ProfileService(db)
    favorite = profile_service.add_favorite(test_user.id, test_book.id)
    
    assert favorite is not None
    assert favorite.user_id == test_user.id
    assert favorite.book_id == test_book.id

def test_add_favorite_nonexistent_book(db, test_user):
    profile_service = ProfileService(db)
    
    with pytest.raises(ValueError):
        profile_service.add_favorite(test_user.id, 999)

def test_remove_favorite(db, test_user, test_book):
    # Create test favorite
    favorite = UserFavorite(
        user_id=test_user.id,
        book_id=test_book.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(favorite)
    db.commit()

    profile_service = ProfileService(db)
    result = profile_service.remove_favorite(test_user.id, test_book.id)
    
    assert result is True
    assert db.query(UserFavorite).count() == 0

def test_remove_nonexistent_favorite(db, test_user, test_book):
    profile_service = ProfileService(db)
    result = profile_service.remove_favorite(test_user.id, test_book.id)
    
    assert result is False

def test_update_last_login(db, test_user):
    profile_service = ProfileService(db)
    
    # Set initial last_login to None
    test_user.last_login = None
    db.commit()
    
    profile_service.update_last_login(test_user.id)
    updated_user = profile_service.get_user_profile(test_user.id)
    
    assert updated_user.last_login is not None
    assert isinstance(updated_user.last_login, datetime)
