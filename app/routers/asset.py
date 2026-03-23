from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.asset import Asset, AssetProcurementLine
from app.models.document import DrawingAsset, Document
from app.models.system import SystemGroup, SystemSubgroup
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetOut,
    AssetProcurementLineCreate, AssetProcurementLineOut,
)

router = APIRouter(tags=["Assets"])


async def _build_asset_out(asset: Asset) -> AssetOut:
    children_count = await Asset.filter(parent_id=asset.id).count()
    data = AssetOut.model_validate(asset, from_attributes=True)
    data.children_count = children_count
    if asset.parent_id:
        parent = await Asset.get_or_none(id=asset.parent_id)
        data.parent_tag = parent.tag if parent else None
    return data


# --- Assets ---

@router.get("/projects/{project_id}/assets", response_model=List[AssetOut])
async def list_assets(
    project_id: int,
    search: Optional[str] = Query(None, description="Search tag or name"),
    site_id: Optional[int] = None,
    status: Optional[str] = None,
    commissioning_status: Optional[str] = None,
    type: Optional[str] = None,
    parent_id: Optional[int] = Query(None, description="Filter by parent asset ID; use 0 for root assets only"),
    subgroup_id: Optional[int] = None,
    group_id: Optional[int] = None,
    discipline_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    filters: dict = {"project_id": project_id}
    if site_id:
        filters["site_id"] = site_id
    if status:
        filters["status"] = status
    if commissioning_status:
        filters["commissioning_status"] = commissioning_status
    if type:
        filters["type"] = type
    if subgroup_id:
        filters["subgroup_id"] = subgroup_id
    elif group_id:
        sg_ids = await SystemSubgroup.filter(group_id=group_id).values_list("id", flat=True)
        filters["subgroup_id__in"] = sg_ids if sg_ids else [-1]
    elif discipline_id:
        g_ids = await SystemGroup.filter(discipline_id=discipline_id).values_list("id", flat=True)
        sg_ids = await SystemSubgroup.filter(group_id__in=g_ids).values_list("id", flat=True) if g_ids else []
        filters["subgroup_id__in"] = sg_ids if sg_ids else [-1]
    if parent_id == 0:
        filters["parent_id"] = None  # root assets only
    elif parent_id:
        filters["parent_id"] = parent_id

    qs = Asset.filter(**filters)

    if search:
        from tortoise.expressions import Q
        qs = qs.filter(Q(tag__icontains=search) | Q(name__icontains=search))

    total = await qs.count()
    assets = await qs.order_by("tag").offset((page - 1) * page_size).limit(page_size)

    return [await _build_asset_out(a) for a in assets]


@router.get("/projects/{project_id}/assets/count")
async def count_assets(project_id: int) -> dict:
    total = await Asset.filter(project_id=project_id).count()
    return {"total": total}


@router.post("/projects/{project_id}/assets", response_model=AssetOut, status_code=201)
async def create_asset(project_id: int, data: AssetCreate):
    asset = await Asset.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return await _build_asset_out(asset)


@router.get("/assets/{asset_id}", response_model=AssetOut)
async def get_asset(asset_id: int):
    asset = await Asset.get_or_none(id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return await _build_asset_out(asset)


@router.patch("/assets/{asset_id}", response_model=AssetOut)
async def update_asset(asset_id: int, data: AssetUpdate):
    asset = await Asset.get_or_none(id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await asset.update_from_dict(data.model_dump(exclude_unset=True)).save()
    return await _build_asset_out(asset)


@router.delete("/assets/{asset_id}", status_code=204)
async def delete_asset(asset_id: int):
    asset = await Asset.get_or_none(id=asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await asset.delete()


@router.get("/assets/{asset_id}/children", response_model=List[AssetOut])
async def list_children(asset_id: int):
    children = await Asset.filter(parent_id=asset_id).order_by("tag")
    return [await _build_asset_out(c) for c in children]


@router.get("/assets/{asset_id}/drawings")
async def get_asset_drawings(asset_id: int) -> list:
    pins = await DrawingAsset.filter(asset_id=asset_id, status="confirmed")
    result = []
    seen_docs = set()
    for pin in pins:
        if pin.document_id in seen_docs:
            continue
        seen_docs.add(pin.document_id)
        doc = await Document.get_or_none(id=pin.document_id)
        if doc:
            result.append({
                "document_id": doc.id,
                "document_name": doc.name,
                "category": doc.category,
                "status": doc.status,
                "page_number": pin.page_number,
                "pin_id": pin.id,
                "x_percent": pin.x_percent,
                "y_percent": pin.y_percent,
            })
    return result


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
