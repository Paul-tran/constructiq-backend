from fastapi import APIRouter, HTTPException
from typing import List

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyOut

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=List[CompanyOut])
async def list_companies():
    return await Company.all()


@router.post("", response_model=CompanyOut, status_code=201)
async def create_company(data: CompanyCreate):
    company = await Company.create(**data.model_dump())
    return company


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(company_id: int):
    company = await Company.get_or_none(id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(company_id: int, data: CompanyUpdate):
    company = await Company.get_or_none(id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await company.update_from_dict(data.model_dump(exclude_none=True)).save()
    return company


@router.delete("/{company_id}", status_code=204)
async def delete_company(company_id: int):
    company = await Company.get_or_none(id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await company.delete()
