from datetime import datetime
from typing import Union, List, Literal
from pydantic import BaseModel

from spaceone.core import utils

from spaceone.identity.model.user.request import State, AuthType

__all__ = [
    "UserResponse",
    "UsersResponse",
    "UserSummaryResponse",
    "UsersSummaryResponse",
]

RoleType = Literal[
    "SYSTEM_ADMIN", "DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "USER"
]


class UserResponse(BaseModel):
    user_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    email: Union[str, None] = None
    email_verified: Union[bool, None] = None
    auth_type: Union[AuthType, None] = None
    role_type: Union[RoleType, None] = None
    mfa: Union[dict, None] = None
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    api_key_count: Union[int, None] = None
    required_actions: Union[List[str], None] = None
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


class UserSummaryResponse(BaseModel):
    user_id: str
    name: str
    state: State


class UsersSummaryResponse(BaseModel):
    results: List[UserSummaryResponse]
    total_count: int
