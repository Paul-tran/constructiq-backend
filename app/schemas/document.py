from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Document ---

class DocumentCreate(BaseModel):
    project_id: int
    name: str
    category: str = "General"
    drawing_type: Optional[str] = None
    description: Optional[str] = None
    site_id: Optional[int] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    uploaded_by: str


class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    drawing_type: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    site_id: Optional[int] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None


class DocumentOut(BaseModel):
    id: int
    project_id: int
    name: str
    category: str
    drawing_type: Optional[str]
    status: str
    version: str
    description: Optional[str]
    site_id: Optional[int]
    location_id: Optional[int]
    unit_id: Optional[int]
    partition_id: Optional[int]
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- DocumentRevision ---

class DocumentRevisionCreate(BaseModel):
    document_id: int
    version: str
    file_key: str
    file_name: str
    file_size: Optional[int] = None
    uploaded_by: str


class DocumentRevisionOut(BaseModel):
    id: int
    document_id: int
    version: str
    file_key: str
    file_name: str
    file_size: Optional[int]
    status: str
    uploaded_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- DocumentApproval ---

class DocumentApprovalCreate(BaseModel):
    document_id: int
    revision_id: int
    approver_id: str
    decision: str  # approved / rejected
    comments: Optional[str] = None


class DocumentApprovalOut(BaseModel):
    id: int
    document_id: int
    revision_id: int
    approver_id: str
    decision: str
    comments: Optional[str]
    approved_at: datetime

    class Config:
        from_attributes = True


# --- DocumentComment ---

class DocumentCommentCreate(BaseModel):
    document_id: int
    revision_id: int
    user_id: str
    comment: str
    x_percent: Optional[float] = None
    y_percent: Optional[float] = None
    page_number: Optional[int] = None


class DocumentCommentOut(BaseModel):
    id: int
    document_id: int
    revision_id: int
    user_id: str
    comment: str
    x_percent: Optional[float]
    y_percent: Optional[float]
    page_number: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# --- DrawingAsset ---

class DrawingAssetCreate(BaseModel):
    document_id: int
    revision_id: int
    tag: str
    asset_type: Optional[str] = None
    description: Optional[str] = None
    x_percent: float
    y_percent: float
    page_number: int = 1


class DrawingAssetUpdate(BaseModel):
    tag: Optional[str] = None
    asset_type: Optional[str] = None
    description: Optional[str] = None
    x_percent: Optional[float] = None
    y_percent: Optional[float] = None
    page_number: Optional[int] = None
    status: Optional[str] = None
    asset_id: Optional[int] = None


class DrawingAssetOut(BaseModel):
    id: int
    document_id: int
    revision_id: int
    asset_id: Optional[int]
    tag: str
    asset_type: Optional[str]
    description: Optional[str]
    x_percent: float
    y_percent: float
    page_number: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
