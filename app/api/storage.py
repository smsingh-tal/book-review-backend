"""API endpoints for file storage."""
from typing import Optional
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.storage import StorageService
from app.core.auth import get_current_user

router = APIRouter(tags=["storage"])
storage_service = StorageService()

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    subdir: Optional[str] = None,
    current_user = Depends(get_current_user)
) -> dict:
    """
    Upload a file to storage.
    
    Args:
        file: The file to upload
        subdir: Optional subdirectory to store the file in
        current_user: The authenticated user (injected by dependency)
        
    Returns:
        dict: Object containing the file path
    """
    try:
        file_path = await storage_service.save_file(file, subdir)
        return {"file_path": file_path}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@router.delete("/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user = Depends(get_current_user)
) -> dict:
    """
    Delete a file from storage.
    
    Args:
        file_path: Path to the file to delete
        current_user: The authenticated user (injected by dependency)
        
    Returns:
        dict: Success message
    """
    try:
        if storage_service.delete_file(file_path):
            return {"message": "File deleted successfully"}
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )

@router.get("/{file_path:path}")
async def get_file(file_path: str) -> FileResponse:
    """
    Get a file from storage.
    
    Args:
        file_path: Path to the file to retrieve
        
    Returns:
        FileResponse: The requested file
    """
    full_path = storage_service.upload_dir / file_path
    if not full_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    return FileResponse(str(full_path))
