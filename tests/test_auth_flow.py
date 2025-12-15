import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_login_refresh_logout_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # register
        r = await ac.post("/api/auth/register", json={"email":"a@example.com","password":"password123"})
        assert r.status_code in (201,409)

        # login
        r = await ac.post("/api/auth/login", json={"email":"a@example.com","password":"password123"})
        assert r.status_code == 200
        tokens = r.json()
        assert "access_token" in tokens and "refresh_token" in tokens

        # refresh
        r = await ac.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert r.status_code == 200
        new_tokens = r.json()
        assert new_tokens["refresh_token"] != tokens["refresh_token"]

        # logout (revoke)
        r = await ac.post("/api/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
        assert r.status_code == 200
