from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


# --- Project ---

class ProjectCreate(BaseModel):
    company_id: int
    name: str
    number: str
    type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contract_value: Optional[Decimal] = None
    currency: str = "CAD"
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    contractor_name: Optional[str] = None
    contractor_contact: Optional[str] = None
    status: str = "planning"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contract_value: Optional[Decimal] = None
    currency: Optional[str] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    contractor_name: Optional[str] = None
    contractor_contact: Optional[str] = None
    status: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    company_id: int
    name: str
    number: str
    type: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    contract_value: Optional[Decimal]
    currency: str
    client_name: Optional[str]
    client_contact: Optional[str]
    contractor_name: Optional[str]
    contractor_contact: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- ProjectGeographyConfig ---

class ProjectGeographyConfigCreate(BaseModel):
    project_id: int
    level_1_enabled: bool = True
    level_1_name: str = "Site"
    level_2_enabled: bool = True
    level_2_name: str = "Location"
    level_3_enabled: bool = True
    level_3_name: str = "Unit"
    level_4_enabled: bool = True
    level_4_name: str = "Partition"


class ProjectGeographyConfigUpdate(BaseModel):
    level_1_enabled: Optional[bool] = None
    level_1_name: Optional[str] = None
    level_2_enabled: Optional[bool] = None
    level_2_name: Optional[str] = None
    level_3_enabled: Optional[bool] = None
    level_3_name: Optional[str] = None
    level_4_enabled: Optional[bool] = None
    level_4_name: Optional[str] = None


class ProjectGeographyConfigOut(BaseModel):
    id: int
    project_id: int
    level_1_enabled: bool
    level_1_name: str
    level_2_enabled: bool
    level_2_name: str
    level_3_enabled: bool
    level_3_name: str
    level_4_enabled: bool
    level_4_name: str

    class Config:
        from_attributes = True


# --- ProjectCompany ---

class ProjectCompanyCreate(BaseModel):
    project_id: int
    company_id: int
    role: str


class ProjectCompanyOut(BaseModel):
    id: int
    project_id: int
    company_id: int
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True
