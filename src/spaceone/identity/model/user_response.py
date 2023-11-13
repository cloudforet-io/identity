from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.identity.model.user_request import State, UserType, Backend, RoleType

__all__ = ["UserResponse", "UsersResponse"]


class UserResponse(BaseModel):
    user_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    email_verified: Union[bool, None] = None
    user_type: Union[UserType, None] = None
    backend: Union[Backend, None] = None
    role_type: Union[RoleType, None] = None
    mfa: Union[dict, None] = None
    required_actions: Union[List[str], None] = None
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    tags: Union[dict, None] = None
    domain_id: str
    created_at: Union[datetime, None] = None
    last_accessed_at: Union[datetime, None] = None


class UsersResponse(BaseModel):
    results: List[UserResponse]
    total_count: int
