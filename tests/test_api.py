"""
API smoke tests.
Run inside Docker: docker-compose exec api pytest tests/ -v
"""
import pytest


# ── Health ────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.anyio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "ConstructIQ" in response.json()["message"]


# ── Auth rejection ────────────────────────────────────────────────────────────
# These endpoints require a valid Clerk JWT. Without one they must return 403.

PROTECTED_ROUTES = [
    ("GET",  "/api/v1/companies"),
    ("GET",  "/api/v1/projects"),
    ("GET",  "/api/v1/roles"),
    ("GET",  "/api/v1/geography/sites"),
    ("GET",  "/api/v1/billing/subscription"),
]

@pytest.mark.anyio
@pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
async def test_protected_routes_reject_unauthenticated(client, method, path):
    response = await client.request(method, path)
    assert response.status_code in (401, 403), (
        f"{method} {path} should reject unauthenticated requests, got {response.status_code}"
    )


@pytest.mark.anyio
async def test_bad_token_returns_401(client):
    response = await client.get(
        "/api/v1/companies",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code == 401


# ── Webhook is public ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_webhook_is_accessible_without_auth(client):
    # Should not return 401/403 — it has its own Stripe signature check
    response = await client.post(
        "/api/v1/billing/webhook",
        content=b"{}",
        headers={"stripe-signature": "invalid"},
    )
    # 400 = reached the handler (bad signature), not 401/403 (auth)
    assert response.status_code not in (401, 403)
