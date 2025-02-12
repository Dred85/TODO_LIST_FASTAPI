import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_get():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        responce = await ac.get("/")
        assert responce.status_code == 200
        data = responce.json()
        print(data)
        assert data == {"message": "Task Management API"}
