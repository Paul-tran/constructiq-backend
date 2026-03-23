import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, UploadFile, File, status
from typing import Optional

from app.core.auth import (
    get_current_user,
    hash_password,
    verify_password,
    decode_token,
    set_auth_cookies,
    clear_auth_cookies,
    create_access_token,
)
from app.core.email import send_password_reset_email
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserOut,
    UpdateProfileRequest,
    ChangePasswordRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.services.storage import upload_file, get_presigned_url

router = APIRouter(prefix="/auth", tags=["Auth"])

BUCKET = os.getenv("MINIO_BUCKET", "constructiq")


# --- Register ---

@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: RegisterRequest, response: Response):
    existing = await User.get_or_none(email=data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await User.create(
        email=data.email,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    set_auth_cookies(response, user.id)
    return UserOut.model_validate(user, from_attributes=True)


# --- Login ---

@router.post("/login", response_model=UserOut)
async def login(data: LoginRequest, response: Response):
    user = await User.get_or_none(email=data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    set_auth_cookies(response, user.id)
    return UserOut.model_validate(user, from_attributes=True)


# --- Logout ---

@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logged out"}


# --- Refresh ---

@router.post("/refresh", response_model=UserOut)
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload["sub"])
    user = await User.get_or_none(id=user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Issue new access token only (keep refresh token)
    new_access = create_access_token(user.id)
    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=os.getenv("ENVIRONMENT", "development") == "production",
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )
    return UserOut.model_validate(user, from_attributes=True)


# --- Me ---

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user, from_attributes=True)


# --- Update profile ---

@router.patch("/me", response_model=UserOut)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
):
    updates = data.model_dump(exclude_none=True)
    if "email" in updates:
        clash = await User.get_or_none(email=updates["email"])
        if clash and clash.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
    await current_user.update_from_dict(updates).save()
    return UserOut.model_validate(current_user, from_attributes=True)


# --- Change password ---

@router.post("/me/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    await current_user.save()
    return {"message": "Password changed"}


# --- Avatar upload ---

@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    key = f"avatars/{current_user.id}.{ext}"

    content = await file.read()
    upload_file(content, key, file.content_type)

    current_user.avatar_key = key
    await current_user.save()
    return UserOut.model_validate(current_user, from_attributes=True)


# --- Password reset request ---

@router.post("/request-password-reset")
async def request_password_reset(data: PasswordResetRequest):
    user = await User.get_or_none(email=data.email)
    # Always return 200 to avoid user enumeration
    if user:
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await user.save()
        await send_password_reset_email(user.email, token)
    return {"message": "If that email is registered, a reset link has been sent"}


# --- Password reset confirm ---

@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, response: Response):
    user = await User.get_or_none(password_reset_token=data.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user.hashed_password = hash_password(data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    await user.save()

    set_auth_cookies(response, user.id)
    return {"message": "Password reset successfully"}
