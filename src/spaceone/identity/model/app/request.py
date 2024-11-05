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
    "AppCheckRequest",
    "AppSearchQueryRequest",
    "AppStatQueryRequest",
    "State",
    "ResourceGroup",
    "RoleType",
]

State = Literal["ENABLED", "DISABLED", "EXPIRED"]
ResourceGroup = Literal["DOMAIN", "WORKSPACE", "PROJECT"]
RoleType = Literal["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"]


class AppCreateRequest(BaseModel):
    name: str
    role_id: str
    tags: Union[dict, None] = None
    expired_at: Union[str, None] = None
    resource_group: ResourceGroup
    project_id: Union[str, None] = None
    project_group_id: Union[str, None] = None
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


class AppCheckRequest(BaseModel):
    client_id: str
    domain_id: str


class AppSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    app_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    role_type: Union[str, None] = None
    role_id: Union[str, None] = None
    client_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class AppStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
