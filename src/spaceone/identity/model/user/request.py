from typing import Union, Literal, List
from pydantic import BaseModel

__all__ = [
    "UserSearchQueryRequest",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserVerifyEmailRequest",
    "UserStatQueryRequest",
    "UserConfirmEmailRequest",
    "UserResetPasswordRequest",
    "UserSetRequiredActionsRequest",
    "UserEnableMFARequest",
    "UserDisableMFARequest",
    "UserConfirmMFARequest",
    "UserDeleteRequest",
    "UserEnableRequest",
    "UserDisableRequest",
    "UserGetRequest",
    "UserType",
    "AuthType",
    "State",
]

State = Literal["ENABLED", "DISABLED", "PENDING"]
AuthType = Literal["LOCAL", "EXTERNAL"]
UserType = Literal["USER", "API_USER"]


class UserCreateRequest(BaseModel):
    user_id: str
    password: Union[str, None] = None
    name: Union[str, None] = None
    email: Union[str, None] = None
    user_type: Union[UserType, None] = None
    auth_type: AuthType
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    tags: Union[dict, None] = None
    reset_password: Union[bool, None] = None
    role_binding: Union[dict, None] = None
    domain_id: str


class UserUpdateRequest(BaseModel):
    user_id: str
    password: Union[str, None] = None
    name: Union[str, None] = None
    email: Union[str, None] = None
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    tags: Union[dict, None] = None
    reset_password: Union[bool, None] = None
    domain_id: str


class UserVerifyEmailRequest(BaseModel):
    user_id: str
    email: Union[str, None] = None
    force: Union[bool, None] = None
    domain_id: str


class UserConfirmEmailRequest(BaseModel):
    user_id: str
    verify_code: str
    domain_id: str


class UserResetPasswordRequest(BaseModel):
    user_id: str
    domain_id: str


class UserSetRequiredActionsRequest(BaseModel):
    user_id: str
    actions: List[str]
    domain_id: str


class UserEnableMFARequest(BaseModel):
    user_id: str
    mfa_type: str
    options: dict
    domain_id: str


class UserDisableMFARequest(BaseModel):
    user_id: str
    force: Union[bool, None] = None
    domain_id: str


class UserConfirmMFARequest(BaseModel):
    user_id: str
    verify_code: str
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
    user_type: Union[UserType, None] = None
    auth_type: Union[AuthType, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class UserStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
