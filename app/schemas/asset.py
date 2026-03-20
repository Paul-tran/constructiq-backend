from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


# --- Asset ---

class AssetCreate(BaseModel):
    project_id: int
    tag: str
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    site_id: int
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    supplier: Optional[str] = None
    planned_cost: Optional[Decimal] = None
    po_number: Optional[str] = None
    delivery_date: Optional[date] = None
    warranty_expiry: Optional[date] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    supplier: Optional[str] = None
    planned_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    po_number: Optional[str] = None
    delivery_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    commissioning_status: Optional[str] = None


class AssetOut(BaseModel):
    id: int
    project_id: int
    tag: str
    name: Optional[str]
    type: Optional[str]
    status: str
    description: Optional[str]
    site_id: int
    location_id: Optional[int]
    unit_id: Optional[int]
    partition_id: Optional[int]
    manufacturer: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    supplier: Optional[str]
    planned_cost: Optional[Decimal]
    actual_cost: Optional[Decimal]
    po_number: Optional[str]
    delivery_date: Optional[date]
    warranty_expiry: Optional[date]
    commissioning_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- AssetProcurementLine ---

class AssetProcurementLineCreate(BaseModel):
    asset_id: int
    document_id: int
    line_item_number: Optional[int] = None
    description: Optional[str] = None
    amount: Decimal
    mapped_by: str


class AssetProcurementLineOut(BaseModel):
    id: int
    asset_id: int
    document_id: int
    line_item_number: Optional[int]
    description: Optional[str]
    amount: Decimal
    mapped_by: str
    mapped_at: datetime

    class Config:
        from_attributes = True
