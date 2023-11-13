from datetime import datetime
from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "ServiceAccountCreateRequest",
    "ServiceAccountUpdateRequest",
    "ServiceAccountChangeTrustedServiceAccountRequest",
    "ServiceAccountChangeProjectRequest",
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


class ServiceAccountChangeTrustedServiceAccountRequest(BaseModel):
    service_account_id: str
    trusted_service_account_id: str
    workspace_id: str
    domain_id: str


class ServiceAccountChangeProjectRequest(BaseModel):
    service_account_id: str
    project_id: str
    workspace_id: str
    domain_id: str


class ServiceAccountDeleteRequest(BaseModel):
    service_account_id: str
    workspace_id: str
    domain_id: str


class ServiceAccountGetRequest(BaseModel):
    service_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


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


class ServiceAccountStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
