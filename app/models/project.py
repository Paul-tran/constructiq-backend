from tortoise import fields
from tortoise.models import Model

class Project(Model):
    id = fields.IntField(pk=True)
    company = fields.ForeignKeyField("models.Company", related_name="projects")
    name = fields.CharField(max_length=255)
    number = fields.CharField(max_length=100, unique=True)
    type = fields.CharField(max_length=100, null=True)
    start_date = fields.DateField(null=True)
    end_date = fields.DateField(null=True)
    contract_value = fields.DecimalField(max_digits=15, decimal_places=2, null=True)
    currency = fields.CharField(max_length=10, default="CAD")
    client_name = fields.CharField(max_length=255, null=True)
    client_contact = fields.CharField(max_length=255, null=True)
    contractor_name = fields.CharField(max_length=255, null=True)
    contractor_contact = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=50, default="planning")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "projects"

    def __str__(self):
        return self.name


class ProjectGeographyConfig(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="geography_config")
    level_1_enabled = fields.BooleanField(default=True)
    level_1_name = fields.CharField(max_length=100, default="Site")
    level_2_enabled = fields.BooleanField(default=True)
    level_2_name = fields.CharField(max_length=100, default="Location")
    level_3_enabled = fields.BooleanField(default=True)
    level_3_name = fields.CharField(max_length=100, default="Unit")
    level_4_enabled = fields.BooleanField(default=True)
    level_4_name = fields.CharField(max_length=100, default="Partition")

    class Meta:
        table = "project_geography_configs"


class ProjectCompany(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="collaborators")
    company = fields.ForeignKeyField("models.Company", related_name="project_memberships")
    role = fields.CharField(max_length=100)
    joined_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_companies"