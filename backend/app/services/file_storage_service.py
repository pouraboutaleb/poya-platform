import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from ..core.config import settings


class FileStorageService:
    """Service for handling file uploads and storage"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or settings.storage_path)
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Create storage directory if it doesn't exist"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['invoices', 'documents', 'images', 'temp']
        for subdir in subdirs:
            (self.storage_path / subdir).mkdir(exist_ok=True)
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename to prevent conflicts"""
        file_extension = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{unique_id}{file_extension}"
    
    def _get_file_category(self, file_type: str) -> str:
        """Determine file category based on content type"""
        if 'image' in file_type.lower():
            return 'images'
        elif 'pdf' in file_type.lower() or 'document' in file_type.lower():
            return 'documents'
        else:
            return 'documents'  # Default category
    
    def _validate_file_type(self, content_type: str) -> bool:
        """Validate if file type is allowed"""
        return content_type in settings.allowed_file_types
    
    async def save_file(
        self, 
        file: UploadFile, 
        category: Optional[str] = None
    ) -> dict:
        """
        Save uploaded file to storage
        
        Args:
            file: The uploaded file
            category: Optional category (invoices, documents, images, temp)
            
        Returns:
            dict: File information including filename, path, and URL
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have a filename"
            )
        
        # Validate file type
        if file.content_type and not self._validate_file_type(file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} is not allowed"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size too large. Maximum size is {settings.max_file_size // (1024*1024)}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Determine category
        if not category:
            category = self._get_file_category(file.content_type or "")
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)
        file_path = self.storage_path / category / unique_filename
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Generate file URL
            file_url = f"/api/v1/static/{category}/{unique_filename}"
            
            return {
                "original_filename": file.filename,
                "stored_filename": unique_filename,
                "file_path": str(file_path),
                "file_url": file_url,
                "file_size": len(file_content),
                "content_type": file.content_type,
                "category": category
            }
            
        except Exception as e:
            # Clean up on error
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    def delete_file(self, filename: str, category: str = "documents") -> bool:
        """Delete a file from storage"""
        file_path = self.storage_path / category / filename
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_path(self, filename: str, category: str = "documents") -> Optional[Path]:
        """Get the full path to a stored file"""
        file_path = self.storage_path / category / filename
        return file_path if file_path.exists() else None
    
    def get_file_info(self, filename: str, category: str = "documents") -> Optional[dict]:
        """Get information about a stored file"""
        file_path = self.get_file_path(filename, category)
        if not file_path:
            return None
        
        stat = file_path.stat()
        return {
            "filename": filename,
            "file_path": str(file_path),
            "file_size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "category": category
        }


# Create a global instance
file_storage_service = FileStorageService()
