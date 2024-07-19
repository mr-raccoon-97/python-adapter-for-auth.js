import pytest
from datetime import datetime
from datetime import timedelta

from auth.models import Session
from auth.adapters import Sessions

@pytest.mark.asyncio
async def test_sessions(redis):
    sessions = Sessions(redis)
    session = Session(
        token="123",
        user_id=1,
        expires_at=datetime(2026, 1, 1)
    )

    assert isinstance(session.expires_at, int)
    await sessions.add(session)
    assert await sessions.get("123") == session
    session.expires_at = session.expires_at + 5
    await sessions.update(session)
    assert await sessions.get("123") == session
    await sessions.delete("123")
    assert await sessions.get("123") is None