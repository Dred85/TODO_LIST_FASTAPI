import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
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


@pytest.mark.asyncio
async def test_get_tasks():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        responce = await ac.get("/tasks/")
        assert responce.status_code == 200
        data = responce.json()
        print(data)
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_task_id():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        responce = await ac.get("/tasks/2")
        assert responce.status_code == 200
        data = responce.json()
        assert data['title'] == 'Программирование'

@pytest.mark.asyncio
async def test_post_task():
    async with LifespanManager(app):  # Запускаем и завершаем приложение правильно
        async with AsyncClient(transport=ASGITransport(app=app),
                               base_url="http://test") as ac:
            json_data = {
                "title": "Test",
                "description": "Test",
                "status": "pending",
                "importance": "importance"
            }

            response = await ac.post("/tasks/", json=json_data)

            assert response.status_code == 201# Обычно при успешном POST
            data = response.json()
            assert "id" in data  # Проверяем, что в ответе есть ID новой задачи
            assert data["title"] == "Test"


