from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models.user import User
from app.core.limiter import limiter
from app.services.storage import make_file_key, upload_file, get_presigned_url, delete_file

router = APIRouter(prefix="/files", tags=["File Storage"])

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",        # .xlsx
    "application/vnd.ms-excel",
    "text/csv",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class UploadResponse(BaseModel):
    file_key: str
    file_name: str
    file_size: int
    content_type: str


class PresignedUrlResponse(BaseModel):
    url: str
    expires_in: int


@router.post("/upload", response_model=UploadResponse, status_code=201)
@limiter.limit("30/minute")
async def upload(
    request: Request,
    module: str,
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file to storage.
    - `module`: which module this belongs to (documents, commissioning, assets)
    - `project_id`: the project this file belongs to
    Returns a `file_key` to store in the database (DocumentRevision, CommissioningEvidence, etc.)
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, images, Word, Excel, CSV.",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )

    file_key = make_file_key(module, project_id, file.filename)
    upload_file(file_bytes, file_key, file.content_type)

    return UploadResponse(
        file_key=file_key,
        file_name=file.filename,
        file_size=len(file_bytes),
        content_type=file.content_type,
    )


@router.get("/url", response_model=PresignedUrlResponse)
async def get_file_url(
    file_key: str,
    expires: int = 3600,
    current_user: User = Depends(get_current_user),
):
    """
    Get a presigned URL to download or view a file.
    - `file_key`: the key returned from /upload
    - `expires`: seconds until the URL expires (default 1 hour, max 24 hours)
    """
    expires = min(expires, 86400)  # Cap at 24 hours
    url = get_presigned_url(file_key, expires)
    return PresignedUrlResponse(url=url, expires_in=expires)


@router.delete("/delete", status_code=204)
async def delete(
    file_key: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a file from storage by its file_key."""
    delete_file(file_key)
