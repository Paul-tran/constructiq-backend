from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


# --- CommissioningRecord ---

class CommissioningRecordCreate(BaseModel):
    project_id: int
    type: str = "individual"  # individual / system
    name: str
    description: Optional[str] = None
    site_id: Optional[int] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    assigned_to: Optional[str] = None
    witness_id: Optional[str] = None
    created_by: str


class CommissioningRecordUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    witness_id: Optional[str] = None
    overall_status: Optional[Literal["not_started", "in_progress", "completed", "failed"]] = None


class CommissioningRecordOut(BaseModel):
    id: int
    project_id: int
    type: str
    name: str
    description: Optional[str]
    site_id: Optional[int]
    location_id: Optional[int]
    unit_id: Optional[int]
    partition_id: Optional[int]
    assigned_to: Optional[str]
    witness_id: Optional[str]
    overall_status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- CommissioningAsset ---

class CommissioningAssetCreate(BaseModel):
    commissioning_record_id: int
    asset_id: int


class CommissioningAssetOut(BaseModel):
    id: int
    commissioning_record_id: int
    asset_id: int

    class Config:
        from_attributes = True


# --- CommissioningStage ---

class CommissioningStageCreate(BaseModel):
    commissioning_record_id: int
    stage: str  # pre_commissioning / functional / performance / handover


class CommissioningStageUpdate(BaseModel):
    status: Optional[str] = None
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    witness_signature: Optional[str] = None
    signed_at: Optional[datetime] = None
    conditional_acceptance: Optional[bool] = None
    conditional_notes: Optional[str] = None


class CommissioningStageOut(BaseModel):
    id: int
    commissioning_record_id: int
    stage: str
    status: str
    completed_by: Optional[str]
    completed_at: Optional[datetime]
    witness_signature: Optional[str]
    signed_at: Optional[datetime]
    conditional_acceptance: bool
    conditional_notes: Optional[str]

    class Config:
        from_attributes = True


# --- CommissioningChecklistItem ---

class CommissioningChecklistItemCreate(BaseModel):
    stage_id: int
    description: str


class CommissioningChecklistItemUpdate(BaseModel):
    result: Optional[str] = None  # pass / fail / partial
    measured_value: Optional[str] = None
    specified_value: Optional[str] = None
    notes: Optional[str] = None


class CommissioningChecklistItemOut(BaseModel):
    id: int
    stage_id: int
    description: str
    result: Optional[str]
    measured_value: Optional[str]
    specified_value: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


# --- PunchItem ---

class PunchItemCreate(BaseModel):
    commissioning_record_id: int
    stage_id: Optional[int] = None
    description: str
    severity: Literal["critical", "major", "minor"]
    raised_by: str


class PunchItemUpdate(BaseModel):
    status: Optional[Literal["open", "closed"]] = None
    closed_by: Optional[str] = None
    closed_at: Optional[datetime] = None
    closure_notes: Optional[str] = None


class PunchItemOut(BaseModel):
    id: int
    commissioning_record_id: int
    stage_id: Optional[int]
    description: str
    severity: str
    status: str
    raised_by: str
    raised_at: datetime
    closed_by: Optional[str]
    closed_at: Optional[datetime]
    closure_notes: Optional[str]

    class Config:
        from_attributes = True


# --- CommissioningEvidence ---

class CommissioningEvidenceCreate(BaseModel):
    stage_id: int
    type: str  # form / certificate / photo / signature
    document_id: Optional[int] = None
    file_key: Optional[str] = None
    uploaded_by: str


class CommissioningEvidenceOut(BaseModel):
    id: int
    stage_id: int
    type: str
    document_id: Optional[int]
    file_key: Optional[str]
    uploaded_by: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
