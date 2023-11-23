from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "TrustedServiceAccountCreateRequest",
    "TrustedServiceAccountUpdateRequest",
    "TrustedServiceAccountDeleteRequest",
    "TrustedServiceAccountGetRequest",
    "TrustedServiceAccountSearchQueryRequest",
    "TrustedServiceAccountStatQueryRequest",
]

Scope = Literal["DOMAIN", "WORKSPACE"]


class TrustedServiceAccountCreateRequest(BaseModel):
    name: str
    data: dict
    provider: str
    tags: Union[dict, None] = None
    scope: Scope
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedServiceAccountUpdateRequest(BaseModel):
    trusted_service_account_id: str
    name: Union[str, None] = None
    data: Union[dict, None] = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedServiceAccountDeleteRequest(BaseModel):
    trusted_service_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedServiceAccountGetRequest(BaseModel):
    trusted_service_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedServiceAccountSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    trusted_service_account_id: Union[str, None] = None
    name: Union[str, None] = None
    provider: Union[str, None] = None
    scope: Union[Scope, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str
    user_workspaces: Union[list, None] = None


class TrustedServiceAccountStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
    user_workspaces: Union[list, None] = None
