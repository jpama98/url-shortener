import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_shorten():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/api/v1/shorten", json={"original_url": "https://www.amazon.com"})
    assert res.status_code == 200 or res.status_code == 201
