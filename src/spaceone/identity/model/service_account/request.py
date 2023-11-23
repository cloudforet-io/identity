from datetime import datetime
from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "ServiceAccountCreateRequest",
    "ServiceAccountUpdateRequest",
    "ServiceAccountChangeTrustedServiceAccountRequest",
    "ServiceAccountDeleteRequest",
    "ServiceAccountGetRequest",
    "ServiceAccountSearchQueryRequest",
    "ServiceAccountStatQueryRequest",
]


class ServiceAccountCreateRequest(BaseModel):
    name: str
    data: dict
    provider: str
    trusted_service_account_id: Union[str, None] = None
    tags: Union[dict, None] = None
    project_id: str
    workspace_id: str
    domain_id: str


class ServiceAccountUpdateRequest(BaseModel):
    service_account_id: str
    name: Union[str, None] = None
    data: Union[dict, None] = None
    tags: Union[dict, None] = None
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountChangeTrustedServiceAccountRequest(BaseModel):
    service_account_id: str
    trusted_service_account_id: str
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountDeleteRequest(BaseModel):
    service_account_id: str
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountGetRequest(BaseModel):
    service_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    service_account_id: Union[str, None] = None
    name: Union[str, None] = None
    provider: Union[str, None] = None
    has_secret: Union[bool, None] = None
    trusted_service_account_id: Union[str, None] = None
    project_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str
    user_workspaces: Union[list, None] = None
    user_projects: Union[list, None] = None


class ServiceAccountStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
    user_workspaces: Union[list, None] = None
    user_projects: Union[list, None] = None
