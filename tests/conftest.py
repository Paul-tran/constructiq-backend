"""
Test configuration.

Integration tests require the full stack running:
    docker-compose up -d

Run tests with:
    docker-compose exec api pytest tests/ -v
"""
import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Async HTTP client wired to the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
