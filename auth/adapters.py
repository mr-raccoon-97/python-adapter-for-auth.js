from datetime import datetime
from datetime import timedelta
from typing import Optional

from aioredis import Redis

from auth.models import Session

class Sessions:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add(self, session: Session):
        expires_in = session.expires_at - int(datetime.now().timestamp())
        await self.redis.set(session.token, session.user_id, ex=expires_in)

    async def get(self, token: str) -> Optional[Session]:
        user_id = await self.redis.get(token)
        if user_id is None:
            return None
        expires_in = await self.redis.ttl(token) 
        expires_at = int(datetime.now().timestamp()) + expires_in
        return Session(token=token, user_id=user_id, expires_at=expires_at)
    
    async def update(self, session: Session):
        await self.add(session)

    async def delete(self, token: str):
        await self.redis.delete(token)