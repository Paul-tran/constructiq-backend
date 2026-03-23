import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.models.user import Role, RolePermission, ProjectRolePermission, ProjectMember, ProjectInvitation, User
from app.core.auth import get_current_user, require_admin, hash_password
from app.core.email import send_invite_email
from app.schemas.auth import UserOut
from app.schemas.user import (
    RoleCreate, RoleOut,
    RolePermissionCreate, RolePermissionOut,
    ProjectRolePermissionCreate, ProjectRolePermissionOut,
    ProjectMemberCreate, ProjectMemberOut,
    ProjectInvitationCreate, ProjectInvitationOut,
)

router = APIRouter(tags=["Users & Roles"])


# --- Roles ---

@router.get("/roles", response_model=List[RoleOut])
async def list_roles():
    return await Role.all()


@router.post("/roles", response_model=RoleOut, status_code=201)
async def create_role(data: RoleCreate):
    role = await Role.create(**data.model_dump())
    return role


@router.get("/roles/{role_id}", response_model=RoleOut)
async def get_role(role_id: int):
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/roles/{role_id}", response_model=RoleOut)
async def update_role(role_id: int, data: RoleCreate, _admin: User = Depends(require_admin)):
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role.name = data.name
    await role.save()
    return role


@router.delete("/roles/{role_id}", status_code=204)
async def delete_role(role_id: int, _admin: User = Depends(require_admin)):
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system_role:
        raise HTTPException(status_code=400, detail="Cannot delete a system role")
    await role.delete()


# --- Role Permissions ---

class PermissionEntry(BaseModel):
    module: str
    action: str
    allowed: bool


@router.get("/roles/{role_id}/permissions", response_model=List[RolePermissionOut])
async def list_role_permissions(role_id: int):
    return await RolePermission.filter(role_id=role_id)


@router.put("/roles/{role_id}/permissions", response_model=List[RolePermissionOut])
async def bulk_save_permissions(
    role_id: int,
    entries: List[PermissionEntry],
    _admin: User = Depends(require_admin),
):
    """Replace all permissions for a role in one shot."""
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await RolePermission.filter(role_id=role_id).delete()
    perms = [
        RolePermission(role_id=role_id, module=e.module, action=e.action, allowed=e.allowed)
        for e in entries
        if e.allowed  # only store allowed=True rows to keep it lean
    ]
    if perms:
        await RolePermission.bulk_create(perms)
    return await RolePermission.filter(role_id=role_id)


# --- Project Role Permission Overrides ---

@router.get("/projects/{project_id}/role-permissions", response_model=List[ProjectRolePermissionOut])
async def list_project_role_permissions(project_id: int):
    return await ProjectRolePermission.filter(project_id=project_id)


@router.post("/projects/{project_id}/role-permissions", response_model=ProjectRolePermissionOut, status_code=201)
async def set_project_role_permission(project_id: int, data: ProjectRolePermissionCreate):
    perm = await ProjectRolePermission.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return perm


@router.delete("/projects/{project_id}/role-permissions/{perm_id}", status_code=204)
async def delete_project_role_permission(project_id: int, perm_id: int):
    perm = await ProjectRolePermission.get_or_none(id=perm_id, project_id=project_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission override not found")
    await perm.delete()


# --- Project Members ---

@router.get("/projects/{project_id}/members/me")
async def get_my_membership(
    project_id: int,
    current_user: User = Depends(get_current_user),
):
    member = await ProjectMember.get_or_none(project_id=project_id, user_id=current_user.id)
    if not member:
        return {"role": None}
    await member.fetch_related("role")
    return {"role": member.role.name, "member_id": member.id}


@router.get("/projects/{project_id}/my-permissions")
async def get_my_permissions(
    project_id: int,
    current_user: User = Depends(get_current_user),
):
    """Return a nested dict of {module: {action: bool}} for the current user's role."""
    # Admins get all permissions
    if current_user.is_admin:
        return {"is_admin": True, "permissions": {}}

    member = await ProjectMember.get_or_none(project_id=project_id, user_id=current_user.id)
    if not member:
        return {"is_admin": False, "permissions": {}}

    perms = await RolePermission.filter(role_id=member.role_id, allowed=True)
    result: dict = {}
    for p in perms:
        result.setdefault(p.module, {})[p.action] = True
    return {"is_admin": False, "permissions": result}


@router.get("/projects/{project_id}/members", response_model=List[ProjectMemberOut])
async def list_project_members(project_id: int):
    return await ProjectMember.filter(project_id=project_id)


@router.post("/projects/{project_id}/members", response_model=ProjectMemberOut, status_code=201)
async def add_project_member(project_id: int, data: ProjectMemberCreate):
    member = await ProjectMember.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return member


@router.patch("/projects/{project_id}/members/{member_id}", response_model=ProjectMemberOut)
async def update_project_member(project_id: int, member_id: int, data: dict):
    member = await ProjectMember.get_or_none(id=member_id, project_id=project_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if "role_id" in data:
        member.role_id = data["role_id"]
    if "status" in data:
        member.status = data["status"]
    await member.save()
    return member


@router.delete("/projects/{project_id}/members/{member_id}", status_code=204)
async def remove_project_member(project_id: int, member_id: int):
    member = await ProjectMember.get_or_none(id=member_id, project_id=project_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    await member.delete()


# --- Project Invitations ---

@router.get("/projects/{project_id}/invitations", response_model=List[ProjectInvitationOut])
async def list_project_invitations(project_id: int):
    return await ProjectInvitation.filter(project_id=project_id)


@router.post("/projects/{project_id}/invitations", response_model=ProjectInvitationOut, status_code=201)
async def create_invitation(project_id: int, data: ProjectInvitationCreate):
    invitation = await ProjectInvitation.create(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    return invitation


@router.patch("/projects/{project_id}/invitations/{inv_id}", response_model=ProjectInvitationOut)
async def update_invitation_status(project_id: int, inv_id: int, status: str):
    invitation = await ProjectInvitation.get_or_none(id=inv_id, project_id=project_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    invitation.status = status
    await invitation.save()
    return invitation


@router.delete("/projects/{project_id}/invitations/{inv_id}", status_code=204)
async def delete_invitation(project_id: int, inv_id: int):
    invitation = await ProjectInvitation.get_or_none(id=inv_id, project_id=project_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    await invitation.delete()


# --- Admin: User Management ---

DEFAULT_PROJECT_ID = int(os.getenv("DEFAULT_PROJECT_ID", "1"))


async def _user_out_with_role(user: User) -> UserOut:
    """Build UserOut enriched with the user's role in the default project."""
    out = UserOut.model_validate(user, from_attributes=True)
    member = await ProjectMember.get_or_none(
        project_id=DEFAULT_PROJECT_ID, user_id=user.id
    ).prefetch_related("role")
    if member:
        out.role_id = member.role_id
        out.role_name = member.role.name
    return out


class AdminUserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    project_role_id: Optional[int] = None


@router.get("/admin/users", response_model=List[UserOut])
async def admin_list_users(
    _admin: User = Depends(require_admin),
):
    users = await User.all().order_by("id")
    return [await _user_out_with_role(u) for u in users]


@router.get("/admin/users/{user_id}", response_model=UserOut)
async def admin_get_user(
    user_id: int,
    _admin: User = Depends(require_admin),
):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await _user_out_with_role(user)


@router.patch("/admin/users/{user_id}", response_model=UserOut)
async def admin_update_user(
    user_id: int,
    data: AdminUserUpdate,
    _admin: User = Depends(require_admin),
):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = data.model_dump(exclude_none=True)
    role_id = updates.pop("project_role_id", None)

    if "email" in updates:
        clash = await User.get_or_none(email=updates["email"])
        if clash and clash.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")

    if updates:
        await user.update_from_dict(updates).save()

    if role_id is not None:
        role = await Role.get_or_none(id=role_id)
        if not role:
            raise HTTPException(status_code=400, detail="Role not found")
        member = await ProjectMember.get_or_none(project_id=DEFAULT_PROJECT_ID, user_id=user_id)
        if member:
            member.role_id = role_id
            await member.save()
        else:
            await ProjectMember.create(
                project_id=DEFAULT_PROJECT_ID,
                user_id=user_id,
                role_id=role_id,
                status="active",
            )

    return await _user_out_with_role(user)


@router.delete("/admin/users/{user_id}", status_code=204)
async def admin_delete_user(
    user_id: int,
    current_admin: User = Depends(require_admin),
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()


class InviteUserRequest(BaseModel):
    email: EmailStr
    first_name: str = ""
    last_name: str = ""


@router.post("/admin/users/invite", response_model=UserOut, status_code=201)
async def admin_invite_user(
    data: InviteUserRequest,
    current_admin: User = Depends(require_admin),
):
    existing = await User.get_or_none(email=data.email)
    if existing:
        raise HTTPException(status_code=400, detail="A user with that email already exists")

    token = secrets.token_urlsafe(32)
    user = await User.create(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=hash_password(secrets.token_urlsafe(16)),  # random unusable password
        is_active=True,
        password_reset_token=token,
        password_reset_expires=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    invited_by = f"{current_admin.first_name} {current_admin.last_name}".strip() or current_admin.email
    try:
        await send_invite_email(data.email, invited_by, token)
    except Exception:
        pass  # Don't fail the invite if SMTP is not configured

    return UserOut.model_validate(user, from_attributes=True)
