from typing import AsyncGenerator
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aioredis import Redis

from auth.models import User, Account, Session, VerificationToken
from auth.adapters import Users, Accounts, Sessions, VerificationTokens

def get_session_maker() -> async_sessionmaker[AsyncSession]:
    raise NotImplementedError("You must provide a session maker")

def get_redis() -> Redis:
    raise NotImplementedError("You must provide a Redis connection")

router = APIRouter()

@router.post('/users')
async def create_user(user: User, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)) -> User:
    async with session_maker() as session:
        users = Users(session)
        user = await users.create(user)
        await session.commit()
        return user
    
@router.patch('/users')
async def update_user(user: User, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)) -> User:
    async with session_maker() as session:
        users = Users(session)
        user = await users.update(user)
        await session.commit()
        return user
    
@router.delete('/users/{user_id}')
async def delete_user(user_id: int, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)):
    async with session_maker() as session:
        users = Users(session)
        await users.delete(user_id)
        await session.commit()

@router.get('/users/{user_id}')
async def get_user(user_id: int, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)) -> User:
    async with session_maker() as session:
        users = Users(session)
        user = await users.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
@router.get('/users/emails/{email}')
async def get_user_by_email(email: str, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)) -> User:
    async with session_maker() as session:
        users = Users(session)
        user = await users.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
@router.get('/users/accounts/{account_provider}/{account_id}') 
async def get_user_by_account(account_provider: str, account_id: str, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)) -> User:
    async with session_maker() as session:
        users = Users(session)
        user = await users.get_by_account(account_provider, account_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
@router.post('/users/accounts')
async def link_account(account: Account, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)):
    async with session_maker() as session:
        accounts = Accounts(session)
        account = await accounts.add(account)
        await session.commit()
        return account

@router.delete('/users/accounts/{account_provider}/{account_id}')
async def unlink_account(account_provider: str, account_id: str, session_maker: async_sessionmaker[AsyncSession] = Depends(get_session_maker)):
    async with session_maker() as session:
        accounts = Accounts(session)
        await accounts.remove(account_provider, account_id)
        await session.commit()

@router.post('/users/sessions')
async def create_session(session: Session, redis: Redis = Depends(get_redis)) -> Session:
        sessions = Sessions(redis)
        session = await sessions.add(session)
        return session
    
@router.patch('/users/sessions')
async def update_session(session: Session, redis: Redis = Depends(get_redis)):
    sessions = Sessions(redis)
    await sessions.update(session)
    
@router.delete('/users/sessions/{token}')
async def delete_session(token: str, redis: Redis = Depends(get_redis)):
    sessions = Sessions(redis)
    await sessions.delete(token)
    
@router.get('/users/sessions/{token}')
async def get_session(token: str, redis: Redis = Depends(get_redis)) -> Session:
    sessions = Sessions(redis)
    session = await sessions.get(token)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
    
@router.post('/users/verification')
async def create_verification_token(token: VerificationToken, redis: Redis = Depends(get_redis)) -> VerificationToken:
    tokens = VerificationTokens(redis)
    token = await tokens.add(token)
    return token

class VerificationTokenUse(BaseModel):
    token: str

@router.post('/users/verification/use')
async def use_verification_token(token: VerificationTokenUse, redis: Redis = Depends(get_redis)) -> VerificationToken:
    tokens = VerificationTokens(redis)
    verification_token = await tokens.get(token.token)
    if verification_token is None:
        raise HTTPException(status_code=404, detail="Token not found")
    await tokens.delete(token.token)
    return verification_token