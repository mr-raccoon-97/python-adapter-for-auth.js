import pytest
from datetime import datetime
from datetime import timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import Session, Account, User
from auth.adapters import Sessions, Accounts, Users

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

@pytest.mark.asyncio
async def test_users(session):
    users = Users(session)
    user = User(
        name="test",
        email="test@text.com",
        email_verified_at=datetime(2026, 1, 1),
        image_url="http://test.com"
    )

    user = await users.create(user)
    assert user.id is not None
    assert user.name == "test"
    assert user.email == "test@text.com"
    assert user.email_verified_at == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert user.image_url == "http://test.com"

    json = user.model_dump(by_alias=True)
    assert json["emailVerified"] == "2026-01-01T00:00:00+00:00"
    assert json["image"] == "http://test.com"

    assert await users.get(user.id) == user
    user.name = "test2"
    await users.update(user)
    assert await users.get(user.id) == user

    await users.delete(user.id)
    assert await users.get(user.id) is None