from typing import Optional
from typing import Union
from typing import List
from datetime import datetime
from datetime import timezone
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer
from pydantic import EmailStr

def datetime_to_unix(date: datetime) -> int:
    return int(date.timestamp())

def unix_to_datetime(unix: int, tz=timezone.utc) -> datetime:
    return datetime.fromtimestamp(unix, tz=tz)

class Session(BaseModel):
    token: str = Field(..., serialization_alias="sessionToken")
    user_id: int = Field(..., serialization_alias="userId")
    expires_at: datetime = Field(..., serialization_alias="expires")

    @field_serializer("expires_at")
    def iso_format(expires_at: datetime) -> str:
        return expires_at.isoformat()

class User(BaseModel):
    id: Optional[int] = Field(default=None)
    name: str = Field(...)
    email: EmailStr = Field(...)
    email_verified_at: Optional[datetime] = Field(default=None, serialization_alias="emailVerified")
    image_url: Optional[str] = Field(default=None, serialization_alias="image")

    @field_serializer("email_verified_at")
    def iso_format(email_verified_at: Optional[datetime]) -> Optional[str]:
        if email_verified_at:
            return email_verified_at.isoformat()
        return None
    
class Account(BaseModel):
    id: str = Field(..., serialization_alias="providerAccountId")
    type: str = Field(...)
    provider: str = Field(...)
    user_id: int = Field(..., serialization_alias="userId")
    refresh_token: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None)
    expires_at: Optional[int] = Field(default=None)
    id_token: Optional[str] = Field(default=None)
    scope: Optional[str] = Field(default=None)
    session_state: Optional[str] = Field(default=None)
    token_type: Optional[str] = Field(default=None)

class VerificationToken(BaseModel):
    token: str = Field(...)
    identifier: str = Field(...)
    expires_at: datetime = Field(..., serialization_alias="expires")

    @field_serializer("expires_at")
    def iso_format(expires_at: datetime) -> str:
        return expires_at.isoformat()