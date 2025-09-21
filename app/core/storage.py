"""Storage configuration and utilities."""
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException
from PIL import Image

class StorageConfig:
    """Storage configuration settings."""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FORMATS = {'image/jpeg', 'image/png'}
    UPLOAD_DIR = Path('uploads')
    IMAGE_QUALITY = 85  # For JPEG compression

class StorageService:
    """Service for handling file storage operations."""
    def __init__(self, upload_dir: Optional[Path] = None):
        """Initialize storage service with optional custom upload directory."""
        self.upload_dir = upload_dir or StorageConfig.UPLOAD_DIR
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Ensure the upload directory exists."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file size and format."""
        if file.content_type not in StorageConfig.ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400, 
                detail="File format not supported. Only JPG and PNG are allowed."
            )

    async def _validate_file_size(self, file: UploadFile) -> None:
        """Validate file size."""
        # Read and seek to get file size
        content = await file.read()
        await file.seek(0)  # Reset file position
        
        if len(content) > StorageConfig.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {StorageConfig.MAX_FILE_SIZE/1024/1024}MB"
            )

    def _optimize_image(self, file_path: Path) -> None:
        """Optimize image using PIL."""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                # Save with optimization
                img.save(
                    file_path,
                    quality=StorageConfig.IMAGE_QUALITY,
                    optimize=True
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing image: {str(e)}"
            )

    async def save_file(self, file: UploadFile, subdir: str = "") -> str:
        """
        Save file to storage with validation and optimization.
        
        Args:
            file: The file to save
            subdir: Optional subdirectory within upload dir (e.g., "profiles", "books")
            
        Returns:
            str: The relative path to the saved file
        """
        # Validate file
        self._validate_file(file)
        await self._validate_file_size(file)
        
        # Create unique filename
        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        
        # Setup save path
        save_dir = self.upload_dir / subdir if subdir else self.upload_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / filename
        
        # Save file
        try:
            content = await file.read()
            with open(save_path, "wb") as f:
                f.write(content)
            
            # Optimize image
            self._optimize_image(save_path)
            
            # Return relative path
            return str(Path(subdir) / filename if subdir else filename)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error saving file: {str(e)}"
            )
            
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            bool: True if file was deleted, False if file didn't exist
        """
        full_path = self.upload_dir / file_path
        try:
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting file: {str(e)}"
            )
