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

    await sessions.add(session)
    assert await sessions.get("123") == session
    await sessions.update(session)
    assert await sessions.get("123") == session
    
    json = session.model_dump(by_alias=True) 
    assert json["sessionToken"] == "123"
    assert json["userId"] == 1
    assert json["expires"] == "2026-01-01T00:00:00"

    await sessions.delete("123")
    assert await sessions.get("123") is None