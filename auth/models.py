from typing import Optional
from typing import Union
from typing import List
from datetime import datetime
from datetime import timezone
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer, field_validator
from pydantic import EmailStr
from pydantic import ConfigDict

def datetime_to_unix(date: datetime) -> int:
    return int(date.timestamp())

def unix_to_datetime(unix: int, tz=timezone.utc) -> datetime:
    return datetime.fromtimestamp(unix, tz=tz)

class Model(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

class Session(Model):
    token: str = Field(..., alias="sessionToken")
    user_id: Optional[int] = Field(None, alias="userId")
    expires_at: datetime = Field(..., alias="expires")

    @field_serializer("expires_at")
    def iso_format(expires_at: datetime) -> str:
        return expires_at.isoformat()

class User(Model):
    id: Optional[int] = Field(default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    email_verified_at: Optional[datetime] = Field(default=None, alias="emailVerified")
    image_url: Optional[str] = Field(default=None, alias="image")

    @field_serializer("email_verified_at")
    def iso_format(email_verified_at: Optional[datetime]) -> Optional[str]:
        if email_verified_at:
            return email_verified_at.isoformat()
        return None
    
    
class Account(Model):
    id: str = Field(..., alias="providerAccountId")
    type: str = Field(...)
    provider: str = Field(...)
    user_id: int = Field(..., alias="userId")
    refresh_token: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None)
    expires_at: Optional[int] = Field(default=None)
    id_token: Optional[str] = Field(default=None)
    scope: Optional[str] = Field(default=None)
    session_state: Optional[str] = Field(default=None)
    token_type: Optional[str] = Field(default=None)


class VerificationToken(Model):
    token: str = Field(...)
    identifier: str = Field(...)
    expires_at: datetime = Field(..., alias="expires")

    @field_serializer("expires_at")
    def iso_format(expires_at: datetime) -> str:
        return expires_at.isoformat()