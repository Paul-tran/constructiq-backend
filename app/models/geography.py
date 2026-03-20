from tortoise import fields
from tortoise.models import Model

class Site(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    code = fields.CharField(max_length=50, unique=True)
    address = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "sites"

    def __str__(self):
        return self.name


class Location(Model):
    id = fields.IntField(pk=True)
    site = fields.ForeignKeyField("models.Site", related_name="locations")
    name = fields.CharField(max_length=255)
    code = fields.CharField(max_length=50, null=True)
    is_na = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "locations"

    def __str__(self):
        return self.name


class Unit(Model):
    id = fields.IntField(pk=True)
    location = fields.ForeignKeyField("models.Location", related_name="units")
    name = fields.CharField(max_length=255)
    code = fields.CharField(max_length=50, null=True)
    is_na = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "units"

    def __str__(self):
        return self.name


class Partition(Model):
    id = fields.IntField(pk=True)
    unit = fields.ForeignKeyField("models.Unit", related_name="partitions")
    name = fields.CharField(max_length=255)
    code = fields.CharField(max_length=50, null=True)
    is_na = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "partitions"

    def __str__(self):
        return self.name