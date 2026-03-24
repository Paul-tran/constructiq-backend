from fastapi import APIRouter, HTTPException
from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import os

from app.models.workorder import PMSchedule, PMActivity, WorkOrder, WOType
from app.core.auth import get_current_user
from fastapi import Depends
from app.models.user import User

router = APIRouter(tags=["pm-schedules"])

PROJECT_ID = int(os.getenv("DEFAULT_PROJECT_ID", "1"))


# ── Schemas ───────────────────────────────────────────────────────────────────

class PMActivityCreate(BaseModel):
    name: str
    wo_type_id: Optional[int] = None
    frequency: Literal["weekly", "monthly", "quarterly", "annually", "custom_days"]
    interval_days: Optional[int] = None
    end_date: Optional[date] = None
    description: str = ""


class PMActivityUpdate(BaseModel):
    name: Optional[str] = None
    wo_type_id: Optional[int] = None
    frequency: Optional[Literal["weekly", "monthly", "quarterly", "annually", "custom_days"]] = None
    interval_days: Optional[int] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class PMActivityOut(BaseModel):
    id: int
    name: str
    wo_type_id: Optional[int]
    frequency: str
    interval_days: Optional[int]
    end_date: Optional[date]
    description: str
    next_due_date: Optional[date]
    last_generated_date: Optional[date]
    generated_wo_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class PMScheduleCreate(BaseModel):
    name: str
    asset_id: Optional[int] = None
    site_id: Optional[int] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    assigned_to: Optional[str] = None
    lead_days: int = 7
    start_date: date
    is_active: bool = True
    activities: List[PMActivityCreate] = []


class PMScheduleUpdate(BaseModel):
    name: Optional[str] = None
    asset_id: Optional[int] = None
    site_id: Optional[int] = None
    location_id: Optional[int] = None
    unit_id: Optional[int] = None
    partition_id: Optional[int] = None
    assigned_to: Optional[str] = None
    lead_days: Optional[int] = None
    start_date: Optional[date] = None
    is_active: Optional[bool] = None


class PMScheduleOut(BaseModel):
    id: int
    project_id: int
    name: str
    asset_id: Optional[int]
    site_id: Optional[int]
    location_id: Optional[int]
    unit_id: Optional[int]
    partition_id: Optional[int]
    assigned_to: Optional[str]
    lead_days: int
    start_date: date
    is_active: bool
    activities: List[PMActivityOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _next_due(current: date, frequency: str, interval_days: Optional[int]) -> date:
    if frequency == "weekly":
        return current + timedelta(weeks=1)
    elif frequency == "monthly":
        return current + relativedelta(months=1)
    elif frequency == "quarterly":
        return current + relativedelta(months=3)
    elif frequency == "annually":
        return current + relativedelta(years=1)
    elif frequency == "custom_days" and interval_days:
        return current + timedelta(days=interval_days)
    return current + timedelta(days=30)


async def _activity_out(activity: PMActivity) -> PMActivityOut:
    count = await WorkOrder.filter(pm_activity_id=activity.id).count()
    data = PMActivityOut.model_validate(activity, from_attributes=True)
    data.generated_wo_count = count
    return data


async def _schedule_out(schedule: PMSchedule) -> dict:
    activities = await PMActivity.filter(schedule_id=schedule.id).order_by("created_at")
    acts_out = [await _activity_out(a) for a in activities]
    return {
        "id": schedule.id,
        "project_id": schedule.project_id,
        "name": schedule.name,
        "asset_id": schedule.asset_id,
        "site_id": schedule.site_id,
        "location_id": schedule.location_id,
        "unit_id": schedule.unit_id,
        "partition_id": schedule.partition_id,
        "assigned_to": schedule.assigned_to,
        "lead_days": schedule.lead_days,
        "start_date": str(schedule.start_date),
        "is_active": schedule.is_active,
        "created_at": schedule.created_at.isoformat(),
        "updated_at": schedule.updated_at.isoformat(),
        "activities": [a.model_dump() for a in acts_out],
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/projects/{project_id}/pm-schedules", response_model=List[PMScheduleOut])
async def list_pm_schedules(project_id: int, _: User = Depends(get_current_user)):
    schedules = await PMSchedule.filter(project_id=project_id).order_by("name")
    return [await _schedule_out(s) for s in schedules]


@router.post("/projects/{project_id}/pm-schedules", status_code=201)
async def create_pm_schedule(
    project_id: int,
    data: PMScheduleCreate,
    _: User = Depends(get_current_user),
):
    schedule = await PMSchedule.create(
        project_id=project_id,
        name=data.name,
        asset_id=data.asset_id,
        site_id=data.site_id,
        location_id=data.location_id,
        unit_id=data.unit_id,
        partition_id=data.partition_id,
        assigned_to=data.assigned_to,
        lead_days=data.lead_days,
        start_date=data.start_date,
        is_active=data.is_active,
    )
    for act in data.activities:
        await PMActivity.create(
            schedule_id=schedule.id,
            wo_type_id=act.wo_type_id,
            name=act.name,
            frequency=act.frequency,
            interval_days=act.interval_days,
            end_date=act.end_date,
            description=act.description,
            next_due_date=data.start_date,
        )
    return await _schedule_out(schedule)


@router.get("/pm-schedules/{schedule_id}")
async def get_pm_schedule(schedule_id: int, _: User = Depends(get_current_user)):
    schedule = await PMSchedule.get_or_none(id=schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    return await _schedule_out(schedule)


@router.patch("/pm-schedules/{schedule_id}")
async def update_pm_schedule(
    schedule_id: int,
    data: PMScheduleUpdate,
    _: User = Depends(get_current_user),
):
    schedule = await PMSchedule.get_or_none(id=schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(schedule, field, value)
    await schedule.save()
    return await _schedule_out(schedule)


@router.delete("/pm-schedules/{schedule_id}", status_code=204)
async def delete_pm_schedule(schedule_id: int, _: User = Depends(get_current_user)):
    schedule = await PMSchedule.get_or_none(id=schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    await schedule.delete()


# ── Activity CRUD ─────────────────────────────────────────────────────────────

@router.post("/pm-schedules/{schedule_id}/activities", status_code=201)
async def add_activity(
    schedule_id: int,
    data: PMActivityCreate,
    _: User = Depends(get_current_user),
):
    schedule = await PMSchedule.get_or_none(id=schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    activity = await PMActivity.create(
        schedule_id=schedule_id,
        wo_type_id=data.wo_type_id,
        name=data.name,
        frequency=data.frequency,
        interval_days=data.interval_days,
        end_date=data.end_date,
        description=data.description,
        next_due_date=schedule.start_date,
    )
    return await _activity_out(activity)


@router.patch("/pm-schedules/{schedule_id}/activities/{activity_id}")
async def update_activity(
    schedule_id: int,
    activity_id: int,
    data: PMActivityUpdate,
    _: User = Depends(get_current_user),
):
    activity = await PMActivity.get_or_none(id=activity_id, schedule_id=schedule_id)
    if not activity:
        raise HTTPException(404, "Activity not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(activity, field, value)
    await activity.save()
    return await _activity_out(activity)


@router.delete("/pm-schedules/{schedule_id}/activities/{activity_id}", status_code=204)
async def delete_activity(
    schedule_id: int,
    activity_id: int,
    _: User = Depends(get_current_user),
):
    activity = await PMActivity.get_or_none(id=activity_id, schedule_id=schedule_id)
    if not activity:
        raise HTTPException(404, "Activity not found")
    await activity.delete()


# ── Generate work orders ──────────────────────────────────────────────────────

@router.post("/pm-schedules/{schedule_id}/generate")
async def generate_work_orders(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Generate work orders for all activities that are due (next_due_date - today <= lead_days).
    Returns list of created work order IDs.
    """
    schedule = await PMSchedule.get_or_none(id=schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    if not schedule.is_active:
        raise HTTPException(400, "Schedule is paused")

    today = date.today()
    activities = await PMActivity.filter(schedule_id=schedule_id)
    created_ids = []

    for activity in activities:
        # Skip if past end date
        if activity.end_date and today > activity.end_date:
            continue
        # Skip if not yet due within lead window
        due = activity.next_due_date or schedule.start_date
        if (due - today).days > schedule.lead_days:
            continue

        # Resolve wo_type (fall back to first preventive type for project)
        wo_type_id = activity.wo_type_id
        if not wo_type_id:
            wt = await WOType.filter(project_id=schedule.project_id, category="preventive", is_active=True).first()
            if wt:
                wo_type_id = wt.id

        if not wo_type_id:
            continue  # no PM work order type configured

        wo = await WorkOrder.create(
            project_id=schedule.project_id,
            wo_type_id=wo_type_id,
            pm_activity_id=activity.id,
            title=f"[PM] {activity.name}",
            description=activity.description,
            priority="medium",
            status="open",
            site_id=schedule.site_id,
            location_id=schedule.location_id,
            unit_id=schedule.unit_id,
            partition_id=schedule.partition_id,
            asset_id=schedule.asset_id,
            assigned_to=schedule.assigned_to,
            due_date=due,
            created_by=current_user.email,
        )
        created_ids.append(wo.id)

        # Advance next_due_date
        activity.last_generated_date = today
        activity.next_due_date = _next_due(due, activity.frequency, activity.interval_days)
        await activity.save()

    return {"generated": len(created_ids), "work_order_ids": created_ids}


@router.get("/pm-schedules/{schedule_id}/history")
async def get_schedule_history(schedule_id: int, _: User = Depends(get_current_user)):
    """Return all work orders generated from this schedule."""
    activities = await PMActivity.filter(schedule_id=schedule_id).values_list("id", flat=True)
    wos = await WorkOrder.filter(pm_activity_id__in=list(activities)).order_by("-created_at").prefetch_related("pm_activity")
    return [
        {
            "id": wo.id,
            "title": wo.title,
            "status": wo.status,
            "due_date": wo.due_date,
            "completed_date": wo.completed_date,
            "assigned_to": wo.assigned_to,
            "activity_name": wo.pm_activity.name if wo.pm_activity else None,
        }
        for wo in wos
    ]
