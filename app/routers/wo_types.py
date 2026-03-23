from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.workorder import WOType
from app.schemas.workorder import WOTypeCreate, WOTypeUpdate, WOTypeOut
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["wo-types"])

DEFAULT_WO_TYPES = [
    {"name": "Corrective Maintenance", "category": "corrective", "asset_required": True,  "geography_required": True},
    {"name": "Preventive Maintenance", "category": "preventive", "asset_required": True,  "geography_required": True},
    {"name": "Site Inspection",        "category": "inspection", "asset_required": False, "geography_required": True},
    {"name": "Operations Task",        "category": "operations", "asset_required": False, "geography_required": True},
]


async def seed_default_wo_types(project_id: int):
    """Called when a new project is created to seed the 4 default WO types."""
    for t in DEFAULT_WO_TYPES:
        await WOType.create(project_id=project_id, **t)


@router.get("/projects/{project_id}/wo-types", response_model=List[WOTypeOut])
async def list_wo_types(project_id: int, user: User = Depends(get_current_user)):
    return await WOType.filter(project_id=project_id).order_by("id")


@router.post("/projects/{project_id}/wo-types", response_model=WOTypeOut, status_code=201)
async def create_wo_type(project_id: int, body: WOTypeCreate, user: User = Depends(get_current_user)):
    return await WOType.create(project_id=project_id, **body.model_dump())


@router.patch("/wo-types/{type_id}", response_model=WOTypeOut)
async def update_wo_type(type_id: int, body: WOTypeUpdate, user: User = Depends(get_current_user)):
    wt = await WOType.get_or_none(id=type_id)
    if not wt:
        raise HTTPException(404, "WO type not found")
    await wt.update_from_dict(body.model_dump(exclude_unset=True)).save()
    return wt


@router.delete("/wo-types/{type_id}", status_code=204)
async def delete_wo_type(type_id: int, user: User = Depends(get_current_user)):
    wt = await WOType.get_or_none(id=type_id)
    if not wt:
        raise HTTPException(404, "WO type not found")
    await wt.delete()
