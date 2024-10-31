from datetime import datetime
from typing import Union, List, Literal
from pydantic import BaseModel

from spaceone.core import utils

from spaceone.identity.model.user.request import State, AuthType

__all__ = [
    "UserResponse",
    "UsersResponse",
]

RoleType = Literal["DOMAIN_ADMIN", "USER"]


class UserResponse(BaseModel):
    user_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    email: Union[str, None] = None
    email_verified: Union[bool, None] = None
    auth_type: Union[AuthType, None] = None
    role_id: Union[str, None] = None
    role_type: Union[RoleType, None] = None
    mfa: Union[dict, None] = None
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    required_actions: Union[List[str], None] = None
    refresh_timeout: Union[int, None] = None
    tags: Union[dict, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    last_accessed_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["last_accessed_at"] = utils.datetime_to_iso8601(data["last_accessed_at"])
        return data


class UsersResponse(BaseModel):
    results: List[UserResponse]
    total_count: int
