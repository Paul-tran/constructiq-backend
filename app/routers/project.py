from fastapi import APIRouter, HTTPException
from typing import List

from app.models.project import Project, ProjectGeographyConfig, ProjectCompany
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectOut,
    ProjectGeographyConfigCreate, ProjectGeographyConfigUpdate, ProjectGeographyConfigOut,
    ProjectCompanyCreate, ProjectCompanyOut,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


# --- Projects ---

@router.get("", response_model=List[ProjectOut])
async def list_projects():
    return await Project.all()


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(data: ProjectCreate):
    project = await Project.create(**data.model_dump())
    return project


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: int, data: ProjectUpdate):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await project.update_from_dict(data.model_dump(exclude_none=True)).save()
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int):
    project = await Project.get_or_none(id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await project.delete()


# --- Geography Config ---

@router.get("/{project_id}/geography-config", response_model=ProjectGeographyConfigOut)
async def get_geography_config(project_id: int):
    config = await ProjectGeographyConfig.get_or_none(project_id=project_id)
    if not config:
        raise HTTPException(status_code=404, detail="Geography config not found")
    return config


@router.post("/{project_id}/geography-config", response_model=ProjectGeographyConfigOut, status_code=201)
async def create_geography_config(project_id: int, data: ProjectGeographyConfigCreate):
    existing = await ProjectGeographyConfig.get_or_none(project_id=project_id)
    if existing:
        raise HTTPException(status_code=400, detail="Geography config already exists for this project")
    config = await ProjectGeographyConfig.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return config


@router.patch("/{project_id}/geography-config", response_model=ProjectGeographyConfigOut)
async def update_geography_config(project_id: int, data: ProjectGeographyConfigUpdate):
    config = await ProjectGeographyConfig.get_or_none(project_id=project_id)
    if not config:
        raise HTTPException(status_code=404, detail="Geography config not found")
    await config.update_from_dict(data.model_dump(exclude_none=True)).save()
    return config


# --- Project Companies (collaborators) ---

@router.get("/{project_id}/companies", response_model=List[ProjectCompanyOut])
async def list_project_companies(project_id: int):
    return await ProjectCompany.filter(project_id=project_id)


@router.post("/{project_id}/companies", response_model=ProjectCompanyOut, status_code=201)
async def add_project_company(project_id: int, data: ProjectCompanyCreate):
    entry = await ProjectCompany.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return entry


@router.delete("/{project_id}/companies/{entry_id}", status_code=204)
async def remove_project_company(project_id: int, entry_id: int):
    entry = await ProjectCompany.get_or_none(id=entry_id, project_id=project_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Project company not found")
    await entry.delete()
