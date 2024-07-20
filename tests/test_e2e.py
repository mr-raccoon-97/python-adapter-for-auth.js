import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from aioredis import Redis
from httpx import AsyncClient
from httpx import ASGITransport
from fastapi import FastAPI
from auth.router import router, get_session_maker, get_redis

@pytest.fixture
async def client(sessionmaker: async_sessionmaker[AsyncSession], redis: Redis) -> AsyncGenerator[AsyncClient, None]:
    api = FastAPI()
    api.include_router(router)
    api.dependency_overrides[get_redis] = lambda: redis
    api.dependency_overrides[get_session_maker] = lambda: sessionmaker

    async with AsyncClient(transport=ASGITransport(api), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_users(client: AsyncClient):

    response = await client.post("/users", json={
        "name": "test", 
        "email": "test@test.com",
        "image": "http://test.com"
    })
    assert response.status_code == 200
    user = response.json()
    assert user["id"] is not None
    assert user["name"] == "test"
    assert user["email"] == "test@test.com"

    response = await client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json() == user

    response = await client.get(f"/users/emails/{user['email']}")
    assert response.status_code == 200
    assert response.json() == user

    response = await client.patch("/users", json={
        "id": user["id"],
        "name": "test2",
        "email": "test@test2.com",
        "image": "http://test2.com"
    })

    assert response.status_code == 200

    user = response.json()
    assert user["id"] is not None
    assert user["name"] == "test2"
    assert user["email"] == "test@test2.com"

    await client.delete(f"/users/{user['id']}")

    response = await client.get(f"/users/{user['id']}")
    assert response.status_code == 404

    response = await client.get(f"/users/emails/{user['email']}")
    assert response.status_code == 404



@pytest.mark.asyncio
async def test_accounts(client: AsyncClient):

    response = await client.post("/users", json={
        "name": "test", 
        "email": "test@test.com",
        "image": "http://test.com"
    })

    assert response.status_code == 200
    user = response.json()

    response = await client.post("/users/accounts", json={
        "providerAccountId": "123",
        "type": "test",
        "provider": "google",
        "userId": user["id"]
    })
    assert response.status_code == 200

    response = await client.get("/users/accounts/google/123")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] is not None
    assert user["name"] == "test"
    assert user["email"] == "test@test.com"
    assert user["image"] == "http://test.com"

    await client.delete("/users/accounts/google/123")

    response = await client.get("/users/accounts/google/123")
    assert response.status_code == 404

    response = await client.post("/users/accounts", json={
        "providerAccountId": "123",
        "type": "test",
        "provider": "google",
        "userId": user["id"]
    })
    assert response.status_code == 200

    await client.delete(f"/users/{user['id']}")
    response = await client.get("/users/accounts/google/123")
    assert response.status_code == 404