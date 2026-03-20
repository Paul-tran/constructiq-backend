from tortoise import fields
from tortoise.models import Model


class CommissioningRecord(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="commissioning_records")
    type = fields.CharField(max_length=50, default="individual")
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    site = fields.ForeignKeyField("models.Site", related_name="commissioning_records", null=True)
    location = fields.ForeignKeyField("models.Location", related_name="commissioning_records", null=True)
    unit = fields.ForeignKeyField("models.Unit", related_name="commissioning_records", null=True)
    partition = fields.ForeignKeyField("models.Partition", related_name="commissioning_records", null=True)
    assigned_to = fields.CharField(max_length=255, null=True)
    witness_id = fields.CharField(max_length=255, null=True)
    overall_status = fields.CharField(max_length=50, default="not_started")
    created_by = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "commissioning_records"


class CommissioningAsset(Model):
    id = fields.IntField(pk=True)
    commissioning_record = fields.ForeignKeyField("models.CommissioningRecord", related_name="assets")
    asset = fields.ForeignKeyField("models.Asset", related_name="commissioning_records")

    class Meta:
        table = "commissioning_assets"


class CommissioningStage(Model):
    id = fields.IntField(pk=True)
    commissioning_record = fields.ForeignKeyField("models.CommissioningRecord", related_name="stages")
    stage = fields.CharField(max_length=100)
    status = fields.CharField(max_length=50, default="not_started")
    completed_by = fields.CharField(max_length=255, null=True)
    completed_at = fields.DatetimeField(null=True)
    witness_signature = fields.TextField(null=True)
    signed_at = fields.DatetimeField(null=True)
    conditional_acceptance = fields.BooleanField(default=False)
    conditional_notes = fields.TextField(null=True)

    class Meta:
        table = "commissioning_stages"


class CommissioningChecklistItem(Model):
    id = fields.IntField(pk=True)
    stage = fields.ForeignKeyField("models.CommissioningStage", related_name="checklist_items")
    description = fields.TextField()
    result = fields.CharField(max_length=50, null=True)
    measured_value = fields.CharField(max_length=255, null=True)
    specified_value = fields.CharField(max_length=255, null=True)
    notes = fields.TextField(null=True)

    class Meta:
        table = "commissioning_checklist_items"


class PunchItem(Model):
    id = fields.IntField(pk=True)
    commissioning_record = fields.ForeignKeyField("models.CommissioningRecord", related_name="punch_items")
    stage = fields.ForeignKeyField("models.CommissioningStage", related_name="punch_items", null=True)
    description = fields.TextField()
    severity = fields.CharField(max_length=50)
    status = fields.CharField(max_length=50, default="open")
    raised_by = fields.CharField(max_length=255)
    raised_at = fields.DatetimeField(auto_now_add=True)
    closed_by = fields.CharField(max_length=255, null=True)
    closed_at = fields.DatetimeField(null=True)
    closure_notes = fields.TextField(null=True)

    class Meta:
        table = "punch_items"


class CommissioningEvidence(Model):
    id = fields.IntField(pk=True)
    stage = fields.ForeignKeyField("models.CommissioningStage", related_name="evidence")
    type = fields.CharField(max_length=100)
    document = fields.ForeignKeyField("models.Document", related_name="commissioning_evidence", null=True)
    file_key = fields.CharField(max_length=500, null=True)
    uploaded_by = fields.CharField(max_length=255)
    uploaded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "commissioning_evidence"