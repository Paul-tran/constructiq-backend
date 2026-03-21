from fastapi import APIRouter, HTTPException
from typing import List

from app.models.system import SystemLevelConfig, SystemDiscipline, SystemGroup, SystemSubgroup
from app.schemas.system import (
    SystemLevelConfigOut, SystemLevelConfigUpdate,
    SystemDisciplineCreate, SystemDisciplineOut,
    SystemGroupCreate, SystemGroupOut,
    SystemSubgroupCreate, SystemSubgroupOut,
)

router = APIRouter(tags=["Systems"])


# --- Level Config ---

@router.get("/projects/{project_id}/systems/config", response_model=SystemLevelConfigOut)
async def get_level_config(project_id: int):
    config = await SystemLevelConfig.get_or_none(project_id=project_id)
    if not config:
        # Auto-create defaults on first access
        config = await SystemLevelConfig.create(project_id=project_id)
    return config


@router.patch("/projects/{project_id}/systems/config", response_model=SystemLevelConfigOut)
async def update_level_config(project_id: int, data: SystemLevelConfigUpdate):
    config = await SystemLevelConfig.get_or_none(project_id=project_id)
    if not config:
        config = await SystemLevelConfig.create(project_id=project_id)
    await config.update_from_dict(data.model_dump(exclude_none=True)).save()
    return config


# --- Disciplines (Level 1) ---

@router.get("/projects/{project_id}/systems/disciplines", response_model=List[SystemDisciplineOut])
async def list_disciplines(project_id: int):
    return await SystemDiscipline.filter(project_id=project_id).order_by("name")


@router.post("/projects/{project_id}/systems/disciplines", response_model=SystemDisciplineOut, status_code=201)
async def create_discipline(project_id: int, data: SystemDisciplineCreate):
    return await SystemDiscipline.create(project_id=project_id, **data.model_dump())


@router.get("/systems/disciplines/{discipline_id}", response_model=SystemDisciplineOut)
async def get_discipline(discipline_id: int):
    d = await SystemDiscipline.get_or_none(id=discipline_id)
    if not d:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return d


@router.delete("/systems/disciplines/{discipline_id}", status_code=204)
async def delete_discipline(discipline_id: int):
    d = await SystemDiscipline.get_or_none(id=discipline_id)
    if not d:
        raise HTTPException(status_code=404, detail="Discipline not found")
    await d.delete()


# --- Groups (Level 2) ---

@router.get("/systems/disciplines/{discipline_id}/groups", response_model=List[SystemGroupOut])
async def list_groups(discipline_id: int):
    return await SystemGroup.filter(discipline_id=discipline_id).order_by("name")


@router.post("/systems/disciplines/{discipline_id}/groups", response_model=SystemGroupOut, status_code=201)
async def create_group(discipline_id: int, data: SystemGroupCreate):
    discipline = await SystemDiscipline.get_or_none(id=discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return await SystemGroup.create(discipline_id=discipline_id, **data.model_dump())


@router.get("/systems/groups/{group_id}", response_model=SystemGroupOut)
async def get_group(group_id: int):
    g = await SystemGroup.get_or_none(id=group_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    return g


@router.delete("/systems/groups/{group_id}", status_code=204)
async def delete_group(group_id: int):
    g = await SystemGroup.get_or_none(id=group_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    await g.delete()


# --- Subgroups (Level 3) ---

@router.get("/systems/groups/{group_id}/subgroups", response_model=List[SystemSubgroupOut])
async def list_subgroups(group_id: int):
    return await SystemSubgroup.filter(group_id=group_id).order_by("name")


@router.post("/systems/groups/{group_id}/subgroups", response_model=SystemSubgroupOut, status_code=201)
async def create_subgroup(group_id: int, data: SystemSubgroupCreate):
    group = await SystemGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return await SystemSubgroup.create(group_id=group_id, **data.model_dump())


@router.get("/systems/subgroups/{subgroup_id}", response_model=SystemSubgroupOut)
async def get_subgroup(subgroup_id: int):
    s = await SystemSubgroup.get_or_none(id=subgroup_id)
    if not s:
        raise HTTPException(status_code=404, detail="Subgroup not found")
    return s


@router.delete("/systems/subgroups/{subgroup_id}", status_code=204)
async def delete_subgroup(subgroup_id: int):
    s = await SystemSubgroup.get_or_none(id=subgroup_id)
    if not s:
        raise HTTPException(status_code=404, detail="Subgroup not found")
    await s.delete()
