from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "TrustedAccountCreateRequest",
    "TrustedAccountUpdateRequest",
    "TrustedAccountDeleteRequest",
    "TrustedAccountGetRequest",
    "TrustedAccountSearchQueryRequest",
    "TrustedAccountStatQueryRequest",
]

PermissionGroup = Literal["DOMAIN", "WORKSPACE"]


class TrustedAccountCreateRequest(BaseModel):
    name: str
    data: dict
    provider: str
    tags: Union[dict, None] = None
    permission_group: PermissionGroup
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountUpdateRequest(BaseModel):
    trusted_account_id: str
    name: Union[str, None] = None
    data: Union[dict, None] = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountDeleteRequest(BaseModel):
    trusted_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountGetRequest(BaseModel):
    trusted_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    trusted_account_id: Union[str, None] = None
    name: Union[str, None] = None
    provider: Union[str, None] = None
    permission_group: Union[PermissionGroup, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
