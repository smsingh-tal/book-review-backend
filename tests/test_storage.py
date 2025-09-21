"""Tests for storage service."""
import pytest
import os
import asyncio
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
from io import BytesIO
import pytest_asyncio
from fastapi.datastructures import UploadFile as FastAPIUploadFile

from app.core.storage import StorageService, StorageConfig

# Only mark async tests with asyncio
def pytest_collection_modifyitems(items):
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

@pytest.fixture
def test_storage_dir(tmp_path):
    """Create a temporary directory for test storage."""
    return tmp_path / "test_uploads"

@pytest.fixture
def storage_service(test_storage_dir):
    """Create a storage service instance for testing."""
    return StorageService(test_storage_dir)

@pytest.fixture
def test_image():
    """Create a test image."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

@pytest.fixture
def test_upload_file(test_image):
    """Create a test UploadFile."""
    class MockUploadFile:
        def __init__(self, filename, content_type, file):
            self.filename = filename
            self.content_type = content_type
            self.file = file
            
        async def read(self):
            return self.file.getvalue()
            
        async def seek(self, offset):
            self.file.seek(offset)
    
    return MockUploadFile(
        filename="test.jpg",
        content_type="image/jpeg",
        file=test_image
    )

@pytest.mark.asyncio
async def test_save_file_success(storage_service, test_upload_file):
    """Test successful file save."""
    file_path = await storage_service.save_file(test_upload_file)
    assert file_path
    full_path = storage_service.upload_dir / file_path
    assert full_path.exists()
    # Verify it's a valid image
    img = Image.open(full_path)
    assert img.format in ['JPEG', 'PNG']

@pytest.mark.asyncio
async def test_save_file_with_subdir(storage_service, test_upload_file):
    """Test saving file in subdirectory."""
    subdir = "profiles"
    file_path = await storage_service.save_file(test_upload_file, subdir)
    assert subdir in file_path
    full_path = storage_service.upload_dir / file_path
    assert full_path.exists()

@pytest.mark.asyncio
async def test_save_invalid_format(storage_service):
    """Test saving file with invalid format."""
    class MockUploadFile:
        def __init__(self, filename, content_type, file):
            self.filename = filename
            self.content_type = content_type
            self.file = file
            
        async def read(self):
            return self.file.getvalue()
            
        async def seek(self, offset):
            self.file.seek(offset)
    
    invalid_file = MockUploadFile(
        filename="test.txt",
        content_type="text/plain",
        file=BytesIO(b"test content")
    )
    
    with pytest.raises(HTTPException) as exc:
        await storage_service.save_file(invalid_file)
    assert exc.value.status_code == 400
    assert "format not supported" in str(exc.value.detail)

@pytest.mark.asyncio
async def test_save_large_file(storage_service):
    """Test saving file exceeding size limit."""
    class MockUploadFile:
        def __init__(self, filename, content_type, file):
            self.filename = filename
            self.content_type = content_type
            self.file = file
            
        async def read(self):
            return self.file.getvalue()
            
        async def seek(self, offset):
            self.file.seek(offset)
    
    # Create a file larger than the limit
    large_content = BytesIO(b"0" * (StorageConfig.MAX_FILE_SIZE + 1))
    large_file = MockUploadFile(
        filename="large.jpg",
        content_type="image/jpeg",
        file=large_content
    )
    
    with pytest.raises(HTTPException) as exc:
        await storage_service.save_file(large_file)
    assert exc.value.status_code == 400
    assert "size exceeds" in str(exc.value.detail)

def test_delete_file_success(storage_service, test_image):
    """Test successful file deletion."""
    # First save a file
    test_path = storage_service.upload_dir / "test_delete.jpg"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    with open(test_path, "wb") as f:
        f.write(test_image.getvalue())
    
    # Now delete it
    result = storage_service.delete_file("test_delete.jpg")
    assert result is True
    assert not test_path.exists()

def test_delete_nonexistent_file(storage_service):
    """Test deleting a file that doesn't exist."""
    result = storage_service.delete_file("nonexistent.jpg")
    assert result is False

def test_image_optimization(storage_service, test_image):
    """Test that images are optimized on save."""
    # Save original size
    test_path = storage_service.upload_dir / "test_optimize.jpg"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    with open(test_path, "wb") as f:
        f.write(test_image.getvalue())
    original_size = test_path.stat().st_size
    
    # Run optimization
    storage_service._optimize_image(test_path)
    optimized_size = test_path.stat().st_size
    
    # Size should be different (likely smaller) after optimization
    assert original_size != optimized_size
    
    # Verify it's still a valid image
    img = Image.open(test_path)
    assert img.format in ['JPEG', 'PNG']
