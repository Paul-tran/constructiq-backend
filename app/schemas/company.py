from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CompanyCreate(BaseModel):
    name: str
    type: str  # owner / contractor / consultant
    address: Optional[str] = None
    contact_email: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    type: str
    address: Optional[str]
    contact_email: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
