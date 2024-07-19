from typing import Optional
from typing import Union
from typing import List
from datetime import datetime
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator, field_serializer
from pydantic import EmailStr

def datetime_to_unix(date: datetime) -> int:
    return int(date.timestamp())

def unix_to_datetime(unix: int) -> datetime:
    return datetime.fromtimestamp(unix)

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

class Account(BaseModel):
    id: Optional[int] = Field(default=None)
    user_id: int = Field(..., serialization_alias="userId")
    type: str = Field(...)
    provider: str = Field(...)
    provider_account_id: str = Field(..., serialization_alias="providerAccountId")
    refresh_token: Optional[str] = Field(default=None)
    access_token: Optional[str] = Field(default=None)
    expires_at: Optional[int] = Field(default=None)
    id_token: Optional[str] = Field(default=None)
    scope: Optional[str] = Field(default=None)
    session_state: Optional[str] = Field(default=None)
    token_type: Optional[str] = Field(default=None)

class VerificationToken(BaseModel):
    identifier: str = Field(...)
    expires: datetime = Field(...)
    token: str = Field(...)

    @field_serializer("expires")
    def iso_format(expires: datetime) -> str:
        return expires.isoformat()