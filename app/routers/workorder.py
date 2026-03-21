from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.workorder import (
    WorkOrder, WorkOrderComment,
    WOCorrectiveDetail, WOPMDetail, WOPMChecklistItem,
    WOInspectionDetail, WOInspectionChecklistItem,
    WOOperationsDetail, WOOperationsStep,
    WOType,
)
from app.schemas.workorder import (
    WorkOrderCreate, WorkOrderUpdate, WorkOrderOut,
    CommentCreate, CommentOut,
    CorrectiveDetailUpdate, PMDetailUpdate, InspectionDetailUpdate, OperationsDetailUpdate,
    PMChecklistItemUpdate, InspectionChecklistItemUpdate, OperationsStepUpdate,
    PMChecklistItemCreate, InspectionChecklistItemCreate, OperationsStepCreate,
)
from app.core.auth import get_current_user, ClerkUser

router = APIRouter(tags=["work-orders"])


async def _build_wo_out(wo: WorkOrder) -> dict:
    """Fetch all related detail records and build the full response dict."""
    await wo.fetch_related("wo_type")
    data = {
        "id": wo.id,
        "project_id": wo.project_id,
        "wo_type_id": wo.wo_type_id,
        "wo_type": wo.wo_type,
        "title": wo.title,
        "description": wo.description,
        "priority": wo.priority,
        "status": wo.status,
        "site_id": wo.site_id,
        "location_id": wo.location_id,
        "unit_id": wo.unit_id,
        "partition_id": wo.partition_id,
        "asset_id": wo.asset_id,
        "assigned_to": wo.assigned_to,
        "scheduled_date": wo.scheduled_date,
        "due_date": wo.due_date,
        "completed_date": wo.completed_date,
        "labour_hours": float(wo.labour_hours) if wo.labour_hours is not None else None,
        "notes": wo.notes,
        "created_by": wo.created_by,
        "created_at": wo.created_at,
        "updated_at": wo.updated_at,
        "corrective_detail": None,
        "pm_detail": None,
        "inspection_detail": None,
        "operations_detail": None,
    }

    category = wo.wo_type.category

    if category == "corrective":
        cd = await WOCorrectiveDetail.get_or_none(work_order_id=wo.id)
        data["corrective_detail"] = cd

    elif category == "preventive":
        pd = await WOPMDetail.get_or_none(work_order_id=wo.id)
        if pd:
            await pd.fetch_related("checklist_items")
            data["pm_detail"] = pd

    elif category == "inspection":
        idd = await WOInspectionDetail.get_or_none(work_order_id=wo.id)
        if idd:
            await idd.fetch_related("checklist_items")
            data["inspection_detail"] = idd

    elif category == "operations":
        od = await WOOperationsDetail.get_or_none(work_order_id=wo.id)
        if od:
            await od.fetch_related("steps")
            data["operations_detail"] = od

    return data


async def _log_system_comment(wo_id: int, author: str, message: str):
    await WorkOrderComment.create(work_order_id=wo_id, author=author, body=message, is_system=True)


# ---------------------------------------------------------------------------
# Work order CRUD
# ---------------------------------------------------------------------------

@router.get("/projects/{project_id}/work-orders", response_model=List[WorkOrderOut])
async def list_work_orders(project_id: int, user: ClerkUser = Depends(get_current_user)):
    wos = await WorkOrder.filter(project_id=project_id).order_by("-created_at")
    results = []
    for wo in wos:
        results.append(await _build_wo_out(wo))
    return results


@router.post("/projects/{project_id}/work-orders", response_model=WorkOrderOut, status_code=201)
async def create_work_order(project_id: int, body: WorkOrderCreate, user: ClerkUser = Depends(get_current_user)):
    # Validate geography/asset requirements from WO type
    wo_type = await WOType.get_or_none(id=body.wo_type_id)
    if not wo_type:
        raise HTTPException(404, "WO type not found")
    if wo_type.geography_required and not body.site_id:
        raise HTTPException(422, f"A site is required for '{wo_type.name}' work orders")
    if wo_type.asset_required and not body.asset_id:
        raise HTTPException(422, f"An asset is required for '{wo_type.name}' work orders")

    wo = await WorkOrder.create(
        project_id=project_id,
        wo_type_id=body.wo_type_id,
        title=body.title,
        description=body.description,
        priority=body.priority,
        site_id=body.site_id,
        location_id=body.location_id,
        unit_id=body.unit_id,
        partition_id=body.partition_id,
        asset_id=body.asset_id,
        assigned_to=body.assigned_to,
        scheduled_date=body.scheduled_date,
        due_date=body.due_date,
        notes=body.notes,
        created_by=user.user_id,
    )

    # Create type-specific detail record
    category = wo_type.category

    if category == "corrective":
        cd = body.corrective_detail
        await WOCorrectiveDetail.create(
            work_order_id=wo.id,
            fault_description=cd.fault_description if cd else "",
            failure_cause=cd.failure_cause if cd else "unknown",
            resolution=cd.resolution if cd else "",
        )

    elif category == "preventive":
        pd = body.pm_detail
        detail = await WOPMDetail.create(
            work_order_id=wo.id,
            recurrence=pd.recurrence if pd else "one_off",
            last_serviced_date=pd.last_serviced_date if pd else None,
        )
        if pd and pd.checklist_items:
            for item in pd.checklist_items:
                await WOPMChecklistItem.create(pm_detail_id=detail.id, **item.model_dump())

    elif category == "inspection":
        idd = body.inspection_detail
        detail = await WOInspectionDetail.create(
            work_order_id=wo.id,
            condition_rating=idd.condition_rating if idd else None,
            signed_off_by=idd.signed_off_by if idd else None,
        )
        if idd and idd.checklist_items:
            for item in idd.checklist_items:
                await WOInspectionChecklistItem.create(inspection_detail_id=detail.id, **item.model_dump())

    elif category == "operations":
        od = body.operations_detail
        detail = await WOOperationsDetail.create(
            work_order_id=wo.id,
            shift_start=od.shift_start if od else None,
            shift_end=od.shift_end if od else None,
        )
        if od and od.steps:
            for step in od.steps:
                await WOOperationsStep.create(operations_detail_id=detail.id, **step.model_dump())

    await _log_system_comment(wo.id, user.user_id, f"Work order created with status: open")
    return await _build_wo_out(wo)


@router.get("/work-orders/{wo_id}", response_model=WorkOrderOut)
async def get_work_order(wo_id: int, user: ClerkUser = Depends(get_current_user)):
    wo = await WorkOrder.get_or_none(id=wo_id)
    if not wo:
        raise HTTPException(404, "Work order not found")
    return await _build_wo_out(wo)


@router.patch("/work-orders/{wo_id}", response_model=WorkOrderOut)
async def update_work_order(wo_id: int, body: WorkOrderUpdate, user: ClerkUser = Depends(get_current_user)):
    wo = await WorkOrder.get_or_none(id=wo_id)
    if not wo:
        raise HTTPException(404, "Work order not found")

    old_status = wo.status
    update_data = body.model_dump(exclude_unset=True)
    await wo.update_from_dict(update_data).save()

    if "status" in update_data and update_data["status"] != old_status:
        await _log_system_comment(wo.id, user.user_id, f"Status changed from '{old_status}' to '{update_data['status']}'")

    return await _build_wo_out(wo)


@router.delete("/work-orders/{wo_id}", status_code=204)
async def delete_work_order(wo_id: int, user: ClerkUser = Depends(get_current_user)):
    wo = await WorkOrder.get_or_none(id=wo_id)
    if not wo:
        raise HTTPException(404, "Work order not found")
    await wo.delete()


# ---------------------------------------------------------------------------
# Comments / activity log
# ---------------------------------------------------------------------------

@router.get("/work-orders/{wo_id}/comments", response_model=List[CommentOut])
async def list_comments(wo_id: int, user: ClerkUser = Depends(get_current_user)):
    return await WorkOrderComment.filter(work_order_id=wo_id).order_by("created_at")


@router.post("/work-orders/{wo_id}/comments", response_model=CommentOut, status_code=201)
async def add_comment(wo_id: int, body: CommentCreate, user: ClerkUser = Depends(get_current_user)):
    wo = await WorkOrder.get_or_none(id=wo_id)
    if not wo:
        raise HTTPException(404, "Work order not found")
    return await WorkOrderComment.create(work_order_id=wo_id, author=user.user_id, body=body.body, is_system=False)


# ---------------------------------------------------------------------------
# Type-specific detail patches
# ---------------------------------------------------------------------------

@router.patch("/work-orders/{wo_id}/corrective-detail", response_model=WorkOrderOut)
async def update_corrective_detail(wo_id: int, body: CorrectiveDetailUpdate, user: ClerkUser = Depends(get_current_user)):
    cd = await WOCorrectiveDetail.get_or_none(work_order_id=wo_id)
    if not cd:
        raise HTTPException(404, "Corrective detail not found")
    await cd.update_from_dict(body.model_dump(exclude_unset=True)).save()
    wo = await WorkOrder.get(id=wo_id)
    return await _build_wo_out(wo)


@router.patch("/work-orders/{wo_id}/pm-detail", response_model=WorkOrderOut)
async def update_pm_detail(wo_id: int, body: PMDetailUpdate, user: ClerkUser = Depends(get_current_user)):
    pd = await WOPMDetail.get_or_none(work_order_id=wo_id)
    if not pd:
        raise HTTPException(404, "PM detail not found")
    await pd.update_from_dict(body.model_dump(exclude_unset=True)).save()
    wo = await WorkOrder.get(id=wo_id)
    return await _build_wo_out(wo)


@router.patch("/work-orders/{wo_id}/inspection-detail", response_model=WorkOrderOut)
async def update_inspection_detail(wo_id: int, body: InspectionDetailUpdate, user: ClerkUser = Depends(get_current_user)):
    idd = await WOInspectionDetail.get_or_none(work_order_id=wo_id)
    if not idd:
        raise HTTPException(404, "Inspection detail not found")
    await idd.update_from_dict(body.model_dump(exclude_unset=True)).save()
    wo = await WorkOrder.get(id=wo_id)
    return await _build_wo_out(wo)


@router.patch("/work-orders/{wo_id}/operations-detail", response_model=WorkOrderOut)
async def update_operations_detail(wo_id: int, body: OperationsDetailUpdate, user: ClerkUser = Depends(get_current_user)):
    od = await WOOperationsDetail.get_or_none(work_order_id=wo_id)
    if not od:
        raise HTTPException(404, "Operations detail not found")
    await od.update_from_dict(body.model_dump(exclude_unset=True)).save()
    wo = await WorkOrder.get(id=wo_id)
    return await _build_wo_out(wo)


# ---------------------------------------------------------------------------
# Checklist / step item patches
# ---------------------------------------------------------------------------

@router.patch("/pm-checklist-items/{item_id}", response_model=PMChecklistItemUpdate)
async def update_pm_checklist_item(item_id: int, body: PMChecklistItemUpdate, user: ClerkUser = Depends(get_current_user)):
    item = await WOPMChecklistItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    item.is_checked = body.is_checked
    await item.save()
    return body


@router.post("/pm-details/{detail_id}/checklist-items", status_code=201)
async def add_pm_checklist_item(detail_id: int, body: PMChecklistItemCreate, user: ClerkUser = Depends(get_current_user)):
    return await WOPMChecklistItem.create(pm_detail_id=detail_id, **body.model_dump())


@router.delete("/pm-checklist-items/{item_id}", status_code=204)
async def delete_pm_checklist_item(item_id: int, user: ClerkUser = Depends(get_current_user)):
    item = await WOPMChecklistItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    await item.delete()


@router.patch("/inspection-checklist-items/{item_id}")
async def update_inspection_checklist_item(item_id: int, body: InspectionChecklistItemUpdate, user: ClerkUser = Depends(get_current_user)):
    item = await WOInspectionChecklistItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    item.result = body.result
    await item.save()
    return body


@router.post("/inspection-details/{detail_id}/checklist-items", status_code=201)
async def add_inspection_checklist_item(detail_id: int, body: InspectionChecklistItemCreate, user: ClerkUser = Depends(get_current_user)):
    return await WOInspectionChecklistItem.create(inspection_detail_id=detail_id, **body.model_dump())


@router.delete("/inspection-checklist-items/{item_id}", status_code=204)
async def delete_inspection_checklist_item(item_id: int, user: ClerkUser = Depends(get_current_user)):
    item = await WOInspectionChecklistItem.get_or_none(id=item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    await item.delete()


@router.patch("/operations-steps/{step_id}")
async def update_operations_step(step_id: int, body: OperationsStepUpdate, user: ClerkUser = Depends(get_current_user)):
    step = await WOOperationsStep.get_or_none(id=step_id)
    if not step:
        raise HTTPException(404, "Step not found")
    step.is_completed = body.is_completed
    await step.save()
    return body


@router.post("/operations-details/{detail_id}/steps", status_code=201)
async def add_operations_step(detail_id: int, body: OperationsStepCreate, user: ClerkUser = Depends(get_current_user)):
    return await WOOperationsStep.create(operations_detail_id=detail_id, **body.model_dump())


@router.delete("/operations-steps/{step_id}", status_code=204)
async def delete_operations_step(step_id: int, user: ClerkUser = Depends(get_current_user)):
    step = await WOOperationsStep.get_or_none(id=step_id)
    if not step:
        raise HTTPException(404, "Step not found")
    await step.delete()
