from tortoise import fields
from tortoise.models import Model


class Asset(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="assets")
    tag = fields.CharField(max_length=100)
    name = fields.CharField(max_length=255, null=True)
    type = fields.CharField(max_length=100, null=True)
    status = fields.CharField(max_length=50, default="active")
    description = fields.TextField(null=True)
    site = fields.ForeignKeyField("models.Site", related_name="assets")
    location = fields.ForeignKeyField("models.Location", related_name="assets", null=True)
    unit = fields.ForeignKeyField("models.Unit", related_name="assets", null=True)
    partition = fields.ForeignKeyField("models.Partition", related_name="assets", null=True)
    manufacturer = fields.CharField(max_length=255, null=True)
    model = fields.CharField(max_length=255, null=True)
    serial_number = fields.CharField(max_length=255, null=True)
    supplier = fields.CharField(max_length=255, null=True)
    planned_cost = fields.DecimalField(max_digits=15, decimal_places=2, null=True)
    actual_cost = fields.DecimalField(max_digits=15, decimal_places=2, null=True)
    po_number = fields.CharField(max_length=100, null=True)
    delivery_date = fields.DateField(null=True)
    warranty_expiry = fields.DateField(null=True)
    commissioning_status = fields.CharField(max_length=50, default="not_started")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "assets"
        unique_together = (("tag", "site_id", "location_id", "unit_id", "partition_id"),)

    def __str__(self):
        return f"{self.tag} — {self.name}"


class AssetProcurementLine(Model):
    id = fields.IntField(pk=True)
    asset = fields.ForeignKeyField("models.Asset", related_name="procurement_lines")
    document = fields.ForeignKeyField("models.Document", related_name="procurement_lines")
    line_item_number = fields.IntField(null=True)
    description = fields.TextField(null=True)
    amount = fields.DecimalField(max_digits=15, decimal_places=2)
    mapped_by = fields.CharField(max_length=255)
    mapped_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "asset_procurement_lines"