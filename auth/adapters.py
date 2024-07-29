from datetime import datetime
from datetime import timezone
from typing import Optional

from aioredis import Redis
from sqlalchemy.sql import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from auth.models import Session, datetime_to_unix, unix_to_datetime
from auth.models import Account, User, VerificationToken, Credential
from auth.schemas import accounts, users, credentials

class Sessions:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add(self, session: Session) -> Session:
        expires_in = datetime_to_unix(session.expires_at) - datetime_to_unix(datetime.now())
        await self.redis.set(session.token, session.user_id, ex=expires_in)
        return session

    async def get(self, token: str) -> Optional[Session]:
        user_id = await self.redis.get(token)
        if user_id is None:
            return None
        expires_at = await self.redis.ttl(token) + datetime_to_unix(datetime.now())
        return Session(token=token, user_id=user_id, expires_at=unix_to_datetime(expires_at, tz=timezone.utc))
    
    async def update(self, session: Session) -> Session:
        await self.redis.expire(session.token, datetime_to_unix(session.expires_at) - datetime_to_unix(datetime.now()))
        return session

    async def delete(self, token: str):
        await self.redis.delete(token)

class Users:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        command = insert(users).values(
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            image_url=user.image_url
        ).returning(
            users.columns['id'],
            users.columns['name'],
            users.columns['email'],
            users.columns['email_verified_at'],
            users.columns['image_url']
        )
        result = await self.session.execute(command)
        row = result.fetchone()
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            email_verified_at=row[3],
            image_url=row[4]
        )
    
    async def get(self, id: int) -> Optional[User]:
        command = select(users).where(users.columns['id'] == id)
        result = await self.session.execute(command)
        row = result.fetchone()
        if row is None:
            return None
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            email_verified_at=row[3],
            image_url=row[4]
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        command = select(users).where(users.columns['email'] == email)
        result = await self.session.execute(command)
        row = result.fetchone()
        if row is None:
            return None
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            email_verified_at=row[3],
            image_url=row[4]
        )
    
    async def get_by_account(self, provider: str, id: str) -> Optional[User]:
        command = select(users).join(accounts).where(
            accounts.columns['account_provider'] == provider,
            accounts.columns['account_id'] == id
        )
        result = await self.session.execute(command)
        row = result.fetchone()
        if row is None:
            return None
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            email_verified_at=row[3],
            image_url=row[4]
        )
    
    async def update(self, user: User) -> User:
        command = update(users).where(users.columns['id'] == user.id).values(
            name=user.name,
            email=user.email,
            email_verified_at=user.email_verified_at,
            image_url=user.image_url
        ).returning(
            users.columns['id'],
            users.columns['name'],
            users.columns['email'],
            users.columns['email_verified_at'],
            users.columns['image_url']
        )
        result = await self.session.execute(command)
        row = result.fetchone()
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            email_verified_at=row[3],
            image_url=row[4]
        )
    
    async def delete(self, id: int):
        command = delete(users).where(users.columns['id'] == id)
        await self.session.execute(command)

class Accounts:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, account: Account) -> Account:
        command = insert(accounts).values(
            account_id=account.id,
            account_type=account.type,
            account_provider=account.provider,
            refresh_token=account.refresh_token,
            access_token=account.access_token,
            expires_at=account.expires_at,
            id_token=account.id_token,
            scope=account.scope,
            session_state=account.session_state,
            token_type=account.token_type,
            user_id=account.user_id
        )
        await self.session.execute(command)
        return account

    async def remove(self, provider: str, id: str):
        command = delete(accounts).where(
            accounts.columns['account_provider'] == provider,
            accounts.columns['account_id'] == id
        )
        await self.session.execute(command)


class VerificationTokens:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add(self, verification_token: VerificationToken) -> VerificationToken:
        expires_in = datetime_to_unix(verification_token.expires_at) - datetime_to_unix(datetime.now())
        await self.redis.set(verification_token.token, verification_token.identifier, ex=expires_in)
        return verification_token

    async def get(self, token: str) -> Optional[VerificationToken]:
        identifier = await self.redis.get(token)
        if identifier is None:
            return None
        expires_at = await self.redis.ttl(token) + datetime_to_unix(datetime.now())
        return VerificationToken(token=token, identifier=identifier, expires_at=unix_to_datetime(expires_at, tz=timezone.utc))
    
    async def update(self, verification_token: VerificationToken):
        await self.add(verification_token)
    
    async def delete(self, token: str):
        await self.redis.delete(token)


#TODO:CRYPTOGRAPHY WILL BE A SETTING IN THE FUTURE AND WON'T BE IN THE DATA LAYER. THIS IS JUST FIRST ITERATION.
#HASHING WILL BE DONE IN THE ENDPOINT IN THE PYDANTIC MODEL SO THE PASSWORD WILL NEVER GET IN THE SERVER. 
#FOR NOW IS JUST FOR THE SAKE OF DATABASE DESIGN.

CRYPTOGRAPHY_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')

class Credentials:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.criptography = CRYPTOGRAPHY_CONTEXT

    async def add(self, credential: Credential):
        command = insert(credentials).values(
            user_id=credential.user_id,
            username=credential.username,
            password=self.criptography.hash(credential.password.get_secret_value())
        )
        await self.session.execute(command)        

    async def verify(self, credential: Credential) -> bool:
        query = select(credentials).where(
            credentials.columns['username'] == credential.username,
        )
        result = await self.session.execute(query)
        row = result.fetchone()
        return self.criptography.verify(credential.password.get_secret_value(), row[3]) if row is not None else False
    
    async def remove(self, credential: Credential):
        command = delete(credentials).where(credentials.columns['username'] == credential.username)
        await self.session.execute(command)