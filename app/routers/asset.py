from fastapi import APIRouter, HTTPException
from typing import List

from app.models.asset import Asset, AssetProcurementLine
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetOut,
    AssetProcurementLineCreate, AssetProcurementLineOut,
)

router = APIRouter(tags=["Assets"])


# --- Assets ---

@router.get("/projects/{project_id}/assets", response_model=List[AssetOut])
async def list_assets(project_id: int):
    return await Asset.filter(project_id=project_id)


@router.post("/projects/{project_id}/assets", response_model=AssetOut, status_code=201)
async def create_asset(project_id: int, data: AssetCreate):
    asset = await Asset.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return asset


@router.get("/assets/{asset_id}", response_model=AssetOut)
async def get_asset(asset_id: int):
    asset = await Asset.get_or_none(id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.patch("/assets/{asset_id}", response_model=AssetOut)
async def update_asset(asset_id: int, data: AssetUpdate):
    asset = await Asset.get_or_none(id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await asset.update_from_dict(data.model_dump(exclude_none=True)).save()
    return asset


@router.delete("/assets/{asset_id}", status_code=204)
async def delete_asset(asset_id: int):
    asset = await Asset.get_or_none(id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await asset.delete()


# --- Procurement Lines ---

@router.get("/assets/{asset_id}/procurement-lines", response_model=List[AssetProcurementLineOut])
async def list_procurement_lines(asset_id: int):
    return await AssetProcurementLine.filter(asset_id=asset_id)


@router.post("/assets/{asset_id}/procurement-lines", response_model=AssetProcurementLineOut, status_code=201)
async def create_procurement_line(asset_id: int, data: AssetProcurementLineCreate):
    line = await AssetProcurementLine.create(asset_id=asset_id, **data.model_dump(exclude={"asset_id"}))
    return line


@router.delete("/procurement-lines/{line_id}", status_code=204)
async def delete_procurement_line(line_id: int):
    line = await AssetProcurementLine.get_or_none(id=line_id)
    if not line:
        raise HTTPException(status_code=404, detail="Procurement line not found")
    await line.delete()
