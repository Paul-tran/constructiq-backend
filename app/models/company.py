from tortoise import fields
from tortoise.models import Model

class Company(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    type = fields.CharField(max_length=50)  # owner/contractor/consultant
    address = fields.TextField(null=True)
    contact_email = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "companies"

    def __str__(self):
        return self.name