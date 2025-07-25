from typing import Union, Literal, List
from pydantic import BaseModel

__all__ = [
    "UserSearchQueryRequest",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserVerifyEmailRequest",
    "UserStatQueryRequest",
    "UserSetRequiredActionsRequest",
    "UserSetRefreshTimeout",
    "UserDisableMFARequest",
    "UserDeleteRequest",
    "UserEnableRequest",
    "UserDisableRequest",
    "UserGetRequest",
    "AuthType",
    "State",
]

State = Literal["ENABLED", "DISABLED", "PENDING"]
AuthType = Literal["LOCAL", "EXTERNAL"]
MFAType = Literal["OTP", "EMAIL"]
MFAEnforceState = Literal["ENABLED", "DISABLED"]


class UserCreateRequest(BaseModel):
    user_id: str
    password: Union[str, None] = None
    name: Union[str, None] = ""
    email: Union[str, None] = ""
    auth_type: AuthType
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    tags: Union[dict, None] = None
    reset_password: Union[bool, None] = False
    domain_id: str
    enforce_mfa_state: Union[MFAEnforceState, None] = None
    enforce_mfa_type: Union[MFAType, None] = None


class UserUpdateRequest(BaseModel):
    user_id: str
    password: Union[str, None] = None
    name: Union[str, None] = None
    email: Union[str, None] = None
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    tags: Union[dict, None] = None
    reset_password: Union[bool, None] = False
    domain_id: str
    enforce_mfa_state: Union[MFAEnforceState, None] = None
    enforce_mfa_type: Union[MFAType, None] = None


class UserVerifyEmailRequest(BaseModel):
    user_id: str
    email: Union[str, None] = None
    domain_id: str


class UserDisableMFARequest(BaseModel):
    user_id: str
    domain_id: str


class UserSetRequiredActionsRequest(BaseModel):
    user_id: str
    required_actions: List[str]
    domain_id: str


class UserSetRefreshTimeout(BaseModel):
    user_id: str
    refresh_timeout: int
    domain_id: str


class UserDeleteRequest(BaseModel):
    user_id: str
    domain_id: str


class UserEnableRequest(BaseModel):
    user_id: str
    domain_id: str


class UserDisableRequest(BaseModel):
    user_id: str
    domain_id: str


class UserGetRequest(BaseModel):
    user_id: str
    domain_id: str


class UserSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    user_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    email: Union[str, None] = None
    auth_type: Union[AuthType, None] = None
    domain_id: str


class UserStatQueryRequest(BaseModel):
    query: dict
    domain_id: str
