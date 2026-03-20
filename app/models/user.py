from tortoise import fields
from tortoise.models import Model

class Role(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    is_system_role = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "roles"

    def __str__(self):
        return self.name


class RolePermission(Model):
    id = fields.IntField(pk=True)
    role = fields.ForeignKeyField("models.Role", related_name="permissions")
    module = fields.CharField(max_length=100)
    action = fields.CharField(max_length=100)
    allowed = fields.BooleanField(default=False)

    class Meta:
        table = "role_permissions"


class ProjectRolePermission(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="role_overrides")
    role = fields.ForeignKeyField("models.Role", related_name="project_overrides")
    module = fields.CharField(max_length=100)
    action = fields.CharField(max_length=100)
    allowed = fields.BooleanField(default=False)

    class Meta:
        table = "project_role_permissions"


class ProjectMember(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="members")
    clerk_user_id = fields.CharField(max_length=255)
    company = fields.ForeignKeyField("models.Company", related_name="project_members", null=True)
    role = fields.ForeignKeyField("models.Role", related_name="project_members")
    status = fields.CharField(max_length=50, default="active")
    joined_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_members"


class ProjectInvitation(Model):
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField("models.Project", related_name="invitations")
    email = fields.CharField(max_length=255)
    role = fields.ForeignKeyField("models.Role", related_name="invitations")
    invited_by = fields.CharField(max_length=255)
    status = fields.CharField(max_length=50, default="pending")
    expires_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_invitations"