from tortoise import fields
from tortoise.models import Model


class SystemLevelConfig(Model):
    """Stores admin-configurable level names for the 3-tier system hierarchy per project."""
    id = fields.IntField(pk=True)
    project_id = fields.IntField(unique=True)
    level1_name = fields.CharField(max_length=100, default="Discipline")
    level2_name = fields.CharField(max_length=100, default="System")
    level3_name = fields.CharField(max_length=100, default="Subsystem")

    class Meta:
        table = "system_level_configs"


class SystemDiscipline(Model):
    """Level 1 — e.g. Mechanical, Electrical, Civil"""
    id = fields.IntField(pk=True)
    project_id = fields.IntField()
    name = fields.CharField(max_length=200)
    code = fields.CharField(max_length=50)

    class Meta:
        table = "system_disciplines"


class SystemGroup(Model):
    """Level 2 — e.g. HVAC, Plumbing, Power Distribution"""
    id = fields.IntField(pk=True)
    discipline: fields.ForeignKeyRelation[SystemDiscipline] = fields.ForeignKeyField(
        "models.SystemDiscipline", related_name="groups", on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=200)
    code = fields.CharField(max_length=50)

    class Meta:
        table = "system_groups"


class SystemSubgroup(Model):
    """Level 3 — e.g. Air Handling, Chilled Water, Lighting"""
    id = fields.IntField(pk=True)
    group: fields.ForeignKeyRelation[SystemGroup] = fields.ForeignKeyField(
        "models.SystemGroup", related_name="subgroups", on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=200)
    code = fields.CharField(max_length=50)

    class Meta:
        table = "system_subgroups"
