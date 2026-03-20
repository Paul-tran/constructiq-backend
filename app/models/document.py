from tortoise import fields
from tortoise.models import Model


class Document(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="documents")
    name = fields.CharField(max_length=255)
    category = fields.CharField(max_length=100, default="General")
    drawing_type = fields.CharField(max_length=100, null=True)
    status = fields.CharField(max_length=50, default="draft")
    version = fields.CharField(max_length=50, default="v1.0")
    description = fields.TextField(null=True)
    site = fields.ForeignKeyField("models.Site", related_name="documents", null=True)
    location = fields.ForeignKeyField("models.Location", related_name="documents", null=True)
    unit = fields.ForeignKeyField("models.Unit", related_name="documents", null=True)
    partition = fields.ForeignKeyField("models.Partition", related_name="documents", null=True)
    uploaded_by = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "documents"

    def __str__(self):
        return self.name


class DocumentRevision(Model):
    id = fields.IntField(pk=True)
    document = fields.ForeignKeyField("models.Document", related_name="revisions")
    version = fields.CharField(max_length=50)
    file_key = fields.CharField(max_length=500)
    file_name = fields.CharField(max_length=255)
    file_size = fields.IntField(null=True)
    status = fields.CharField(max_length=50, default="draft")
    uploaded_by = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "document_revisions"


class DocumentApproval(Model):
    id = fields.IntField(pk=True)
    document = fields.ForeignKeyField("models.Document", related_name="approvals")
    revision = fields.ForeignKeyField("models.DocumentRevision", related_name="approvals")
    approver_id = fields.CharField(max_length=255)
    decision = fields.CharField(max_length=50)
    comments = fields.TextField(null=True)
    approved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "document_approvals"


class DocumentComment(Model):
    id = fields.IntField(pk=True)
    document = fields.ForeignKeyField("models.Document", related_name="comments")
    revision = fields.ForeignKeyField("models.DocumentRevision", related_name="comments")
    user_id = fields.CharField(max_length=255)
    comment = fields.TextField()
    x_percent = fields.FloatField(null=True)
    y_percent = fields.FloatField(null=True)
    page_number = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "document_comments"


class DrawingAsset(Model):
    id = fields.IntField(pk=True)
    document = fields.ForeignKeyField("models.Document", related_name="drawing_assets")
    revision = fields.ForeignKeyField("models.DocumentRevision", related_name="drawing_assets")
    asset = fields.ForeignKeyField("models.Asset", related_name="drawing_pins", null=True)
    tag = fields.CharField(max_length=100)
    asset_type = fields.CharField(max_length=100, null=True)
    description = fields.TextField(null=True)
    x_percent = fields.FloatField()
    y_percent = fields.FloatField()
    page_number = fields.IntField(default=1)
    status = fields.CharField(max_length=50, default="pending")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "drawing_assets"