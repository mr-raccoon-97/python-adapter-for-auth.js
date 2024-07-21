import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from aioredis import from_url
from auth.router import router, get_redis, get_session_maker

database_url = URL.create(
    drivername = 'postgresql+asyncpg',
    username = 'test',
    password = 'test',
    host = socket.gethostbyname('postgres'),
    port = 5432,
    database = 'test'
)   
redis_host = socket.gethostbyname('redis')
redis_url = f'redis://{redis_host}:6379/0' 

engine = create_async_engine(database_url)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
redis = from_url(redis_url)

api = FastAPI(root_path='/auth')
api.include_router(router)
api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'], 
)

api.dependency_overrides[get_session_maker] = lambda: sessionmaker
api.dependency_overrides[get_redis] = lambda: redis

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(api, host='0.0.0.0', port=8000, reload=True)