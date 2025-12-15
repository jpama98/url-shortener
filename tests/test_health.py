import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_docs_available():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/docs")
        assert r.status_code in (200, 307)
