from fastapi import APIRouter, HTTPException, status, UploadFile, File, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
from ...services.file_storage_service import file_storage_service
from ...core.security import get_current_user
from ...models.user import User

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = "documents",
    current_user: User = Depends(get_current_user)
):
    """
    Generic file upload endpoint
    
    Args:
        file: The file to upload
        category: Optional category (invoices, documents, images, temp)
        current_user: The authenticated user
    """
    try:
        file_info = await file_storage_service.save_file(file, category)
        return {
            "message": "File uploaded successfully",
            "file_info": file_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/static/{category}/{filename}")
async def serve_file(category: str, filename: str):
    """
    Serve static files from storage
    
    Args:
        category: File category (invoices, documents, images, temp)
        filename: The filename to serve
    """
    # Validate category
    valid_categories = ['invoices', 'documents', 'images', 'temp']
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Get file path
    file_path = file_storage_service.get_file_path(filename, category)
    
    if not file_path or not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Determine media type based on file extension
    media_type = None
    suffix = file_path.suffix.lower()
    
    if suffix in ['.jpg', '.jpeg']:
        media_type = 'image/jpeg'
    elif suffix == '.png':
        media_type = 'image/png'
    elif suffix == '.pdf':
        media_type = 'application/pdf'
    elif suffix in ['.doc', '.docx']:
        media_type = 'application/msword'
    elif suffix in ['.xls', '.xlsx']:
        media_type = 'application/vnd.ms-excel'
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename
    )

@router.get("/files/{category}")
async def list_files(
    category: str,
    current_user: User = Depends(get_current_user)
):
    """
    List all files in a category
    
    Args:
        category: File category to list
        current_user: The authenticated user
    """
    # Validate category
    valid_categories = ['invoices', 'documents', 'images', 'temp']
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    storage_path = Path(file_storage_service.storage_path) / category
    
    if not storage_path.exists():
        return []
    
    files = []
    for file_path in storage_path.iterdir():
        if file_path.is_file():
            file_info = file_storage_service.get_file_info(file_path.name, category)
            if file_info:
                files.append(file_info)
    
    return files

@router.delete("/files/{category}/{filename}")
async def delete_file(
    category: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file from storage
    
    Args:
        category: File category
        filename: The filename to delete
        current_user: The authenticated user
    """
    # Validate category
    valid_categories = ['invoices', 'documents', 'images', 'temp']
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    success = file_storage_service.delete_file(filename, category)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or could not be deleted"
        )
    
    return {"message": "File deleted successfully"}
