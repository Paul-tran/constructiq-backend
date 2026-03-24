from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import date, datetime, time


# ---------------------------------------------------------------------------
# WO Types
# ---------------------------------------------------------------------------

class WOTypeCreate(BaseModel):
    name: str
    category: Literal["corrective", "preventive", "inspection", "operations"]
    asset_required: bool = False
    geography_levels_required: List[str] = []  # e.g. ["site", "location", "unit", "partition"]


class WOTypeUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[Literal["corrective", "preventive", "inspection", "operations"]] = None
    asset_required: Optional[bool] = None
    geography_levels_required: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WOTypeOut(BaseModel):
    id: int
    project_id: int
    name: str
    category: str
    asset_required: bool
    geography_levels_required: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Checklist / Step items
# ---------------------------------------------------------------------------

class PMChecklistItemCreate(BaseModel):
    description: str
    order_index: int = 0


class PMChecklistItemOut(BaseModel):
    id: int
    description: str
    is_checked: bool
    order_index: int

    class Config:
        from_attributes = True


class InspectionChecklistItemCreate(BaseModel):
    description: str
    order_index: int = 0


class InspectionChecklistItemOut(BaseModel):
    id: int
    description: str
    result: str
    order_index: int

    class Config:
        from_attributes = True


class OperationsStepCreate(BaseModel):
    description: str
    order_index: int = 0


class OperationsStepOut(BaseModel):
    id: int
    description: str
    is_completed: bool
    order_index: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Type-specific detail schemas
# ---------------------------------------------------------------------------

class CorrectiveDetailCreate(BaseModel):
    fault_description: str = ""
    failure_cause: Literal["wear", "damage", "operator_error", "unknown", "other"] = "unknown"
    resolution: str = ""


class CorrectiveDetailOut(BaseModel):
    id: int
    fault_description: str
    failure_cause: str
    resolution: str

    class Config:
        from_attributes = True


class PMDetailCreate(BaseModel):
    recurrence: Literal["one_off", "weekly", "monthly", "quarterly", "annually"] = "one_off"
    last_serviced_date: Optional[date] = None
    checklist_items: List[PMChecklistItemCreate] = []


class PMDetailOut(BaseModel):
    id: int
    recurrence: str
    last_serviced_date: Optional[date]
    checklist_items: List[PMChecklistItemOut] = []

    class Config:
        from_attributes = True


class InspectionDetailCreate(BaseModel):
    condition_rating: Optional[int] = None
    signed_off_by: Optional[str] = None
    checklist_items: List[InspectionChecklistItemCreate] = []


class InspectionDetailOut(BaseModel):
    id: int
    condition_rating: Optional[int]
    signed_off_by: Optional[str]
    checklist_items: List[InspectionChecklistItemOut] = []

    class Config:
        from_attributes = True


class OperationsDetailCreate(BaseModel):
    shift_start: Optional[time] = None
    shift_end: Optional[time] = None
    steps: List[OperationsStepCreate] = []


class OperationsDetailOut(BaseModel):
    id: int
    shift_start: Optional[time]
    shift_end: Optional[time]
    steps: List[OperationsStepOut] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Work Order
# ---------------------------------------------------------------------------

class WorkOrderCreate(BaseModel):
    wo_type_id: int
    title: str
    description: str = ""
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    site_id: Optional[int] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    asset_id: Optional[int] = None
    assigned_to: Optional[str] = None
    scheduled_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: str = ""
    # Type-specific details
    corrective_detail: Optional[CorrectiveDetailCreate] = None
    pm_detail: Optional[PMDetailCreate] = None
    inspection_detail: Optional[InspectionDetailCreate] = None
    operations_detail: Optional[OperationsDetailCreate] = None


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Optional[Literal["open", "assigned", "in_progress", "on_hold", "completed", "cancelled"]] = None
    site_id: Optional[int] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    asset_id: Optional[int] = None
    assigned_to: Optional[str] = None
    scheduled_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    labour_hours: Optional[float] = None
    notes: Optional[str] = None


class WorkOrderOut(BaseModel):
    id: int
    project_id: int
    wo_type_id: int
    wo_type: Optional[WOTypeOut] = None
    title: str
    description: str
    priority: str
    status: str
    site_id: Optional[int]
    location_id: Optional[int]
    unit_id: Optional[int]
    partition_id: Optional[int]
    asset_id: Optional[int]
    assigned_to: Optional[str]
    scheduled_date: Optional[date]
    due_date: Optional[date]
    completed_date: Optional[date]
    labour_hours: Optional[float]
    notes: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    # Type-specific details (populated on detail endpoint)
    corrective_detail: Optional[CorrectiveDetailOut] = None
    pm_detail: Optional[PMDetailOut] = None
    inspection_detail: Optional[InspectionDetailOut] = None
    operations_detail: Optional[OperationsDetailOut] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

class CommentCreate(BaseModel):
    body: str


class CommentOut(BaseModel):
    id: int
    author: str
    body: str
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Checklist / step update patches
# ---------------------------------------------------------------------------

class PMChecklistItemUpdate(BaseModel):
    is_checked: bool


class InspectionChecklistItemUpdate(BaseModel):
    result: Literal["pass", "fail", "na"]


class OperationsStepUpdate(BaseModel):
    is_completed: bool


class CorrectiveDetailUpdate(BaseModel):
    fault_description: Optional[str] = None
    failure_cause: Optional[Literal["wear", "damage", "operator_error", "unknown", "other"]] = None
    resolution: Optional[str] = None


class InspectionDetailUpdate(BaseModel):
    condition_rating: Optional[int] = None
    signed_off_by: Optional[str] = None


class PMDetailUpdate(BaseModel):
    recurrence: Optional[Literal["one_off", "weekly", "monthly", "quarterly", "annually"]] = None
    last_serviced_date: Optional[date] = None


class OperationsDetailUpdate(BaseModel):
    shift_start: Optional[time] = None
    shift_end: Optional[time] = None
