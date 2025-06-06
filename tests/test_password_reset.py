import pytest
from httpx import AsyncClient
from httpx import ASGITransport
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_password_reset_request():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/reset/request", json={"email": "test@example.com"})
        assert response.status_code == 200
        assert "message" in response.json()

@pytest.mark.asyncio
async def test_password_reset_confirm_invalid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        data = {
            "email": "test@example.com",
            "otp": "000000",
            "new_password": "newpassword123"
        }
        response = await ac.post("/reset/confirm", json=data)
        assert response.status_code == 200
        assert "message" in response.json()