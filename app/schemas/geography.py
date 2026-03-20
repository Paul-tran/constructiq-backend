from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Site ---

class SiteCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None


class SiteOut(BaseModel):
    id: int
    name: str
    code: str
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Location ---

class LocationCreate(BaseModel):
    site_id: int
    name: str
    code: Optional[str] = None
    is_na: bool = False


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_na: Optional[bool] = None


class LocationOut(BaseModel):
    id: int
    site_id: int
    name: str
    code: Optional[str]
    is_na: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Unit ---

class UnitCreate(BaseModel):
    location_id: int
    name: str
    code: Optional[str] = None
    is_na: bool = False


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_na: Optional[bool] = None


class UnitOut(BaseModel):
    id: int
    location_id: int
    name: str
    code: Optional[str]
    is_na: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Partition ---

class PartitionCreate(BaseModel):
    unit_id: int
    name: str
    code: Optional[str] = None
    is_na: bool = False


class PartitionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_na: Optional[bool] = None


class PartitionOut(BaseModel):
    id: int
    unit_id: int
    name: str
    code: Optional[str]
    is_na: bool
    created_at: datetime

    class Config:
        from_attributes = True
