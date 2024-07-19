import os
import pytest
import dotenv
import socket
from typing import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncTransaction    

from aioredis import Redis
from aioredis import from_url

dotenv.load_dotenv()

@pytest.fixture
def database_url() -> URL:
    return URL.create(
        drivername = 'postgresql+asyncpg',
        username = 'test',
        password = 'test',
        host = socket.gethostbyname('postgres'),
        port = 5432,
        database = 'test'
    )

@pytest.fixture
async def engine(database_url: URL) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(database_url)
    yield engine
    await engine.dispose()


@pytest.fixture 
async def connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    yield connection
    await transaction.rollback()
    await connection.close()

@pytest.fixture
async def sessionmaker(connection: AsyncConnection)-> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    
@pytest.fixture
async def session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session

@pytest.fixture
def redis_url() -> str:
    host = socket.gethostbyname('redis')
    return f'redis://{host}:6379/0' 

@pytest.fixture
async def redis(redis_url: str) -> AsyncGenerator[Redis, None]:
    redis = await from_url(redis_url)
    yield redis
    await redis.close()
    