from typing import Union

from pydantic import BaseModel

__all__ = [
    "UserProfileUpdateRequest",
    "UserProfileUpdatePasswordRequest",
    "UserProfileVerifyEmailRequest",
    "UserProfileConfirmEmailRequest",
    "UserProfileResetPasswordRequest",
    "UserProfileEnableMFARequest",
    "UserProfileDisableMFARequest",
    "UserProfileConfirmMFARequest",
    "UserProfileGetRequest",
    "UserProfileGetWorkspacesRequest",
    "UserProfileGetWorkspaceGroupsRequest",
]


class UserProfileUpdateRequest(BaseModel):
    user_id: str
    name: Union[str, None] = None
    email: Union[str, None] = None
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class UserProfileUpdatePasswordRequest(BaseModel):
    user_id: str
    current_password: Union[str, None] = None
    new_password: str
    required_actions: Union[list, None] = None
    domain_id: str


class UserProfileVerifyEmailRequest(BaseModel):
    user_id: str
    email: Union[str, None] = None
    domain_id: str


class UserProfileConfirmEmailRequest(BaseModel):
    user_id: str
    verify_code: str
    domain_id: str


class UserProfileResetPasswordRequest(BaseModel):
    user_id: str
    domain_id: str


class UserProfileEnableMFARequest(BaseModel):
    user_id: str
    mfa_type: str
    options: dict
    domain_id: str


class UserProfileDisableMFARequest(BaseModel):
    user_id: str
    domain_id: str


class UserProfileConfirmMFARequest(BaseModel):
    user_id: str
    verify_code: str
    domain_id: str


class UserProfileGetRequest(BaseModel):
    user_id: str
    domain_id: str


class UserProfileGetWorkspacesRequest(BaseModel):
    workspace_group_id: Union[str, None] = None
    user_id: str
    domain_id: str


class UserProfileGetWorkspaceGroupsRequest(BaseModel):
    user_id: str
    domain_id: str
