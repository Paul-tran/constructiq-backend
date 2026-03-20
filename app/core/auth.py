import os
import time
import httpx
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "")

security = HTTPBearer()

# Simple in-memory JWKS cache with TTL (1 hour)
_jwks_cache: Optional[dict] = None
_jwks_fetched_at: float = 0
_JWKS_TTL = 3600


@dataclass
class ClerkUser:
    user_id: str   # Clerk's `sub` claim — matches clerk_user_id in our models
    email: Optional[str] = None


async def _fetch_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at

    now = time.time()
    if _jwks_cache and (now - _jwks_fetched_at) < _JWKS_TTL:
        return _jwks_cache

    if not CLERK_JWKS_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLERK_JWKS_URL is not configured",
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(CLERK_JWKS_URL, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_fetched_at = now

    return _jwks_cache


async def verify_clerk_token(token: str) -> ClerkUser:
    try:
        # Peek at the header to find which key to use
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        jwks = await _fetch_jwks()

        signing_key = next(
            (k for k in jwks.get("keys", []) if k.get("kid") == kid),
            None,
        )
        if not signing_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No matching signing key found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Clerk JWTs have no audience by default
        )

        return ClerkUser(
            user_id=payload["sub"],
            email=payload.get("email"),
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> ClerkUser:
    """FastAPI dependency — inject this into any route to require auth."""
    return await verify_clerk_token(credentials.credentials)
