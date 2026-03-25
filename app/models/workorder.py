from tortoise import fields, models


class WOType(models.Model):
    """Admin-defined work order types per project."""
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="wo_types")
    name = fields.CharField(max_length=255)
    category = fields.CharField(max_length=30)   # corrective | preventive | inspection | operations
    asset_required = fields.BooleanField(default=False)
    geography_levels_required = fields.JSONField(default=list)  # e.g. ["site", "location", "unit", "partition"]
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "wo_types"


class WorkOrder(models.Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="work_orders")
    wo_type = fields.ForeignKeyField("models.WOType", related_name="work_orders")
    title = fields.CharField(max_length=255)
    description = fields.TextField(default="")
    priority = fields.CharField(max_length=20, default="medium")   # low | medium | high | critical
    status = fields.CharField(max_length=30, default="open")       # open | assigned | in_progress | on_hold | completed | cancelled
    # Geography
    site = fields.ForeignKeyField("models.Site", related_name="work_orders", null=True)
    location = fields.ForeignKeyField("models.Location", related_name="work_orders", null=True)
    unit = fields.ForeignKeyField("models.Unit", related_name="work_orders", null=True)
    partition = fields.ForeignKeyField("models.Partition", related_name="work_orders", null=True)
    # Asset
    asset = fields.ForeignKeyField("models.Asset", related_name="work_orders", null=True)
    # Assignment & scheduling
    assigned_to = fields.CharField(max_length=255, null=True)
    scheduled_date = fields.DateField(null=True)
    due_date = fields.DateField(null=True)
    completed_date = fields.DateField(null=True)
    labour_hours = fields.DecimalField(max_digits=6, decimal_places=2, null=True)
    notes = fields.TextField(default="")
    pm_activity = fields.ForeignKeyField("models.PMActivity", related_name="work_orders", null=True)
    created_by = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "work_orders"


class WorkOrderComment(models.Model):
    id = fields.IntField(pk=True)
    work_order = fields.ForeignKeyField("models.WorkOrder", related_name="comments")
    author = fields.CharField(max_length=255)
    body = fields.TextField()
    is_system = fields.BooleanField(default=False)   # True = auto-logged status change
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "work_order_comments"


# --- Corrective details ---

class WOCorrectiveDetail(models.Model):
    id = fields.IntField(pk=True)
    work_order = fields.OneToOneField("models.WorkOrder", related_name="corrective_detail")
    fault_description = fields.TextField(default="")
    failure_cause = fields.CharField(max_length=50, default="unknown")  # wear | damage | operator_error | unknown | other
    resolution = fields.TextField(default="")

    class Meta:
        table = "wo_corrective_details"


# --- Preventive maintenance details ---

class WOPMDetail(models.Model):
    id = fields.IntField(pk=True)
    work_order = fields.OneToOneField("models.WorkOrder", related_name="pm_detail")
    recurrence = fields.CharField(max_length=20, default="one_off")  # one_off | weekly | monthly | quarterly | annually
    last_serviced_date = fields.DateField(null=True)

    class Meta:
        table = "wo_pm_details"


class WOPMChecklistItem(models.Model):
    id = fields.IntField(pk=True)
    pm_detail = fields.ForeignKeyField("models.WOPMDetail", related_name="checklist_items")
    description = fields.CharField(max_length=500)
    is_checked = fields.BooleanField(default=False)
    order_index = fields.IntField(default=0)

    class Meta:
        table = "wo_pm_checklist_items"


# --- Inspection details ---

class WOInspectionDetail(models.Model):
    id = fields.IntField(pk=True)
    work_order = fields.OneToOneField("models.WorkOrder", related_name="inspection_detail")
    condition_rating = fields.IntField(null=True)   # 1–5
    signed_off_by = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "wo_inspection_details"


class WOInspectionChecklistItem(models.Model):
    id = fields.IntField(pk=True)
    inspection_detail = fields.ForeignKeyField("models.WOInspectionDetail", related_name="checklist_items")
    description = fields.CharField(max_length=500)
    result = fields.CharField(max_length=10, default="na")  # pass | fail | na
    order_index = fields.IntField(default=0)

    class Meta:
        table = "wo_inspection_checklist_items"


# --- Operations details ---

class WOOperationsDetail(models.Model):
    id = fields.IntField(pk=True)
    work_order = fields.OneToOneField("models.WorkOrder", related_name="operations_detail")
    shift_start = fields.TimeField(null=True)
    shift_end = fields.TimeField(null=True)

    class Meta:
        table = "wo_operations_details"


class WOOperationsStep(models.Model):
    id = fields.IntField(pk=True)
    operations_detail = fields.ForeignKeyField("models.WOOperationsDetail", related_name="steps")
    description = fields.CharField(max_length=500)
    is_completed = fields.BooleanField(default=False)
    order_index = fields.IntField(default=0)

    class Meta:
        table = "wo_operations_steps"


# --- PM Schedules ---

class PMSchedule(models.Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="pm_schedules")
    name = fields.CharField(max_length=255)
    assets = fields.ManyToManyField(
        "models.Asset",
        related_name="pm_schedules",
        through="pm_schedule_assets",
        forward_key="asset_id",
        backward_key="schedule_id",
    )
    site_id = fields.IntField(null=True)
    location_id = fields.IntField(null=True)
    unit_id = fields.IntField(null=True)
    partition_id = fields.IntField(null=True)
    assigned_to = fields.CharField(max_length=255, null=True)
    lead_days = fields.IntField(default=7)
    start_date = fields.DateField()
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "pm_schedules"


class PMActivity(models.Model):
    id = fields.IntField(pk=True)
    schedule = fields.ForeignKeyField("models.PMSchedule", related_name="activities")
    wo_type = fields.ForeignKeyField("models.WOType", related_name="pm_activities", null=True)
    name = fields.CharField(max_length=255)
    frequency = fields.CharField(max_length=50)   # weekly|monthly|quarterly|annually|custom_days
    interval_days = fields.IntField(null=True)     # only used when frequency=custom_days
    end_date = fields.DateField(null=True)
    description = fields.TextField(default="")
    next_due_date = fields.DateField(null=True)
    last_generated_date = fields.DateField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "pm_activities"
