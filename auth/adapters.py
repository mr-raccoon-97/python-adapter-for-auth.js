from datetime import datetime
from datetime import timedelta
from typing import Optional

from aioredis import Redis

from auth.models import Session, datetime_to_unix, unix_to_datetime

class Sessions:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add(self, session: Session):
        expires_in = datetime_to_unix(session.expires_at) - datetime_to_unix(datetime.now())
        await self.redis.set(session.token, session.user_id, ex=expires_in)

    async def get(self, token: str) -> Optional[Session]:
        user_id = await self.redis.get(token)
        if user_id is None:
            return None
        expires_at = await self.redis.ttl(token) + datetime_to_unix(datetime.now())
        return Session(token=token, user_id=user_id, expires_at=unix_to_datetime(expires_at))
    
    async def update(self, session: Session):
        await self.add(session)

    async def delete(self, token: str):
        await self.redis.delete(token)