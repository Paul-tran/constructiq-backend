from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Role ---

class RoleCreate(BaseModel):
    name: str
    is_system_role: bool = False


class RoleOut(BaseModel):
    id: int
    name: str
    is_system_role: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- RolePermission ---

class RolePermissionCreate(BaseModel):
    role_id: int
    module: str
    action: str
    allowed: bool = False


class RolePermissionOut(BaseModel):
    id: int
    role_id: int
    module: str
    action: str
    allowed: bool

    class Config:
        from_attributes = True


# --- ProjectRolePermission ---

class ProjectRolePermissionCreate(BaseModel):
    project_id: int
    role_id: int
    module: str
    action: str
    allowed: bool = False


class ProjectRolePermissionOut(BaseModel):
    id: int
    project_id: int
    role_id: int
    module: str
    action: str
    allowed: bool

    class Config:
        from_attributes = True


# --- ProjectMember ---

class ProjectMemberCreate(BaseModel):
    project_id: int
    user_id: int
    company_id: Optional[int] = None
    role_id: int


class ProjectMemberOut(BaseModel):
    id: int
    project_id: int
    user_id: int
    company_id: Optional[int]
    role_id: int
    status: str
    joined_at: datetime

    class Config:
        from_attributes = True


# --- ProjectInvitation ---

class ProjectInvitationCreate(BaseModel):
    project_id: int
    email: str
    role_id: int
    invited_by: str
    expires_at: datetime


class ProjectInvitationOut(BaseModel):
    id: int
    project_id: int
    email: str
    role_id: int
    invited_by: str
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
