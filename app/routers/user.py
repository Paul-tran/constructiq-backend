from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel

from app.models.user import Role, RolePermission, ProjectRolePermission, ProjectMember, ProjectInvitation, User
from app.core.auth import get_current_user, require_admin
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


@router.delete("/roles/{role_id}", status_code=204)
async def delete_role(role_id: int):
    role = await Role.get_or_none(id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await role.delete()


# --- Role Permissions ---

@router.get("/roles/{role_id}/permissions", response_model=List[RolePermissionOut])
async def list_role_permissions(role_id: int):
    return await RolePermission.filter(role_id=role_id)


@router.post("/roles/{role_id}/permissions", response_model=RolePermissionOut, status_code=201)
async def set_role_permission(role_id: int, data: RolePermissionCreate):
    perm = await RolePermission.create(role_id=role_id, **data.model_dump(exclude={"role_id"}))
    return perm


@router.delete("/roles/{role_id}/permissions/{perm_id}", status_code=204)
async def delete_role_permission(role_id: int, perm_id: int):
    perm = await RolePermission.get_or_none(id=perm_id, role_id=role_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    await perm.delete()


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

class AdminUserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


@router.get("/admin/users", response_model=List[UserOut])
async def admin_list_users(
    _admin: User = Depends(require_admin),
):
    return [UserOut.model_validate(u, from_attributes=True) for u in await User.all().order_by("id")]


@router.get("/admin/users/{user_id}", response_model=UserOut)
async def admin_get_user(
    user_id: int,
    _admin: User = Depends(require_admin),
):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user, from_attributes=True)


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
    if "email" in updates:
        clash = await User.get_or_none(email=updates["email"])
        if clash and clash.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
    await user.update_from_dict(updates).save()
    return UserOut.model_validate(user, from_attributes=True)


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
