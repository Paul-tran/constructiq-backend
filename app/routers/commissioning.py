from fastapi import APIRouter, HTTPException
from typing import List

from app.models.commissioning import (
    CommissioningRecord, CommissioningAsset, CommissioningStage,
    CommissioningChecklistItem, PunchItem, CommissioningEvidence,
)
from app.schemas.commissioning import (
    CommissioningRecordCreate, CommissioningRecordUpdate, CommissioningRecordOut,
    CommissioningAssetCreate, CommissioningAssetOut,
    CommissioningStageCreate, CommissioningStageUpdate, CommissioningStageOut,
    CommissioningChecklistItemCreate, CommissioningChecklistItemUpdate, CommissioningChecklistItemOut,
    PunchItemCreate, PunchItemUpdate, PunchItemOut,
    CommissioningEvidenceCreate, CommissioningEvidenceOut,
)

router = APIRouter(tags=["Commissioning"])


# --- Commissioning Records ---

@router.get("/projects/{project_id}/commissioning", response_model=List[CommissioningRecordOut])
async def list_records(project_id: int):
    return await CommissioningRecord.filter(project_id=project_id)


@router.post("/projects/{project_id}/commissioning", response_model=CommissioningRecordOut, status_code=201)
async def create_record(project_id: int, data: CommissioningRecordCreate):
    record = await CommissioningRecord.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return record


@router.get("/commissioning/{record_id}", response_model=CommissioningRecordOut)
async def get_record(record_id: int):
    record = await CommissioningRecord.get_or_none(id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Commissioning record not found")
    return record


@router.patch("/commissioning/{record_id}", response_model=CommissioningRecordOut)
async def update_record(record_id: int, data: CommissioningRecordUpdate):
    record = await CommissioningRecord.get_or_none(id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Commissioning record not found")
    await record.update_from_dict(data.model_dump(exclude_none=True)).save()
    return record


@router.delete("/commissioning/{record_id}", status_code=204)
async def delete_record(record_id: int):
    record = await CommissioningRecord.get_or_none(id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Commissioning record not found")
    await record.delete()


# --- Commissioning Assets (linked assets) ---

@router.get("/commissioning/{record_id}/assets", response_model=List[CommissioningAssetOut])
async def list_commissioning_assets(record_id: int):
    return await CommissioningAsset.filter(commissioning_record_id=record_id)


@router.post("/commissioning/{record_id}/assets", response_model=CommissioningAssetOut, status_code=201)
async def add_commissioning_asset(record_id: int, data: CommissioningAssetCreate):
    entry = await CommissioningAsset.create(commissioning_record_id=record_id, **data.model_dump(exclude={"commissioning_record_id"}))
    return entry


@router.delete("/commissioning/{record_id}/assets/{entry_id}", status_code=204)
async def remove_commissioning_asset(record_id: int, entry_id: int):
    entry = await CommissioningAsset.get_or_none(id=entry_id, commissioning_record_id=record_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Commissioning asset not found")
    await entry.delete()


# --- Commissioning Stages ---

@router.get("/commissioning/{record_id}/stages", response_model=List[CommissioningStageOut])
async def list_stages(record_id: int):
    return await CommissioningStage.filter(commissioning_record_id=record_id)


@router.post("/commissioning/{record_id}/stages", response_model=CommissioningStageOut, status_code=201)
async def create_stage(record_id: int, data: CommissioningStageCreate):
    stage = await CommissioningStage.create(commissioning_record_id=record_id, **data.model_dump(exclude={"commissioning_record_id"}))
    return stage


@router.get("/stages/{stage_id}", response_model=CommissioningStageOut)
async def get_stage(stage_id: int):
    stage = await CommissioningStage.get_or_none(id=stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    return stage


@router.patch("/stages/{stage_id}", response_model=CommissioningStageOut)
async def update_stage(stage_id: int, data: CommissioningStageUpdate):
    stage = await CommissioningStage.get_or_none(id=stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Stage not found")
    await stage.update_from_dict(data.model_dump(exclude_none=True)).save()
    return stage


# --- Checklist Items ---

@router.get("/stages/{stage_id}/checklist", response_model=List[CommissioningChecklistItemOut])
async def list_checklist(stage_id: int):
    return await CommissioningChecklistItem.filter(stage_id=stage_id)


@router.post("/stages/{stage_id}/checklist", response_model=CommissioningChecklistItemOut, status_code=201)
async def create_checklist_item(stage_id: int, data: CommissioningChecklistItemCreate):
    item = await CommissioningChecklistItem.create(stage_id=stage_id, **data.model_dump(exclude={"stage_id"}))
    return item


@router.patch("/checklist/{item_id}", response_model=CommissioningChecklistItemOut)
async def update_checklist_item(item_id: int, data: CommissioningChecklistItemUpdate):
    item = await CommissioningChecklistItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    await item.update_from_dict(data.model_dump(exclude_none=True)).save()
    return item


@router.delete("/checklist/{item_id}", status_code=204)
async def delete_checklist_item(item_id: int):
    item = await CommissioningChecklistItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    await item.delete()


# --- Punch Items ---

@router.get("/commissioning/{record_id}/punch-items", response_model=List[PunchItemOut])
async def list_punch_items(record_id: int):
    return await PunchItem.filter(commissioning_record_id=record_id)


@router.post("/commissioning/{record_id}/punch-items", response_model=PunchItemOut, status_code=201)
async def create_punch_item(record_id: int, data: PunchItemCreate):
    item = await PunchItem.create(commissioning_record_id=record_id, **data.model_dump(exclude={"commissioning_record_id"}))
    return item


@router.patch("/punch-items/{item_id}", response_model=PunchItemOut)
async def update_punch_item(item_id: int, data: PunchItemUpdate):
    item = await PunchItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Punch item not found")
    await item.update_from_dict(data.model_dump(exclude_none=True)).save()
    return item


@router.delete("/punch-items/{item_id}", status_code=204)
async def delete_punch_item(item_id: int):
    item = await PunchItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Punch item not found")
    await item.delete()


# --- Evidence ---

@router.get("/stages/{stage_id}/evidence", response_model=List[CommissioningEvidenceOut])
async def list_evidence(stage_id: int):
    return await CommissioningEvidence.filter(stage_id=stage_id)


@router.post("/stages/{stage_id}/evidence", response_model=CommissioningEvidenceOut, status_code=201)
async def add_evidence(stage_id: int, data: CommissioningEvidenceCreate):
    evidence = await CommissioningEvidence.create(stage_id=stage_id, **data.model_dump(exclude={"stage_id"}))
    return evidence


@router.delete("/evidence/{evidence_id}", status_code=204)
async def delete_evidence(evidence_id: int):
    evidence = await CommissioningEvidence.get_or_none(id=evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    await evidence.delete()
