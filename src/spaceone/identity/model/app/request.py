from datetime import datetime
from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "AppCreateRequest",
    "AppUpdateRequest",
    "AppGenerateAPIKeyRequest",
    "AppEnableRequest",
    "AppDisableRequest",
    "AppDeleteRequest",
    "AppGetRequest",
    "AppSearchQueryRequest",
    "AppStatQueryRequest",
    "State",
    "PermissionGroup",
    "RoleType",
]

State = Literal["ENABLED", "DISABLED", "EXPIRED"]
PermissionGroup = Literal["DOMAIN", "WORKSPACE"]
RoleType = Literal[
    "SYSTEM", "SYSTEM_ADMIN", "DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"
]


class AppCreateRequest(BaseModel):
    name: str
    role_id: str
    tags: Union[dict, None] = None
    expired_at: Union[str, None] = None
    permission_group: PermissionGroup
    workspace_id: Union[str, None] = None
    domain_id: str


class AppUpdateRequest(BaseModel):
    app_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class AppGenerateAPIKeyRequest(BaseModel):
    app_id: str
    workspace_id: Union[str, None] = None
    expired_at: Union[str, None] = None
    domain_id: str


class AppEnableRequest(BaseModel):
    app_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class AppDisableRequest(BaseModel):
    app_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class AppDeleteRequest(BaseModel):
    app_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class AppGetRequest(BaseModel):
    app_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class AppSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    app_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    role_type: Union[str, None] = None
    role_id: Union[str, None] = None
    api_key_id: Union[str, None] = None
    permission_group: Union[PermissionGroup, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class AppStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
