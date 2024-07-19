from typing import Optional
from typing import Union
from typing import List
from datetime import datetime
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator, field_serializer

class Session(BaseModel):
    token: str = Field(..., serialization_alias="sessionToken")
    user_id: int = Field(..., serialization_alias="userId")
    expires_at: Union[int, datetime] = Field(..., serialization_alias="expires")

    @field_validator("expires_at")
    @classmethod
    def expires_at_to_unix(cls, value: Union[int, datetime] ):
        if isinstance(value, datetime):
            return int(value.timestamp())
        return value