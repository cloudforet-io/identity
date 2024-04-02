from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "TrustedAccountCreateRequest",
    "TrustedAccountUpdateRequest",
    "TrustedAccountUpdateSecretRequest",
    "TrustedAccountDeleteRequest",
    "TrustedAccountSyncRequest",
    "TrustedAccountGetRequest",
    "TrustedAccountSearchQueryRequest",
    "TrustedAccountStatQueryRequest",
    "ResourceGroup",
]

ResourceGroup = Literal["DOMAIN", "WORKSPACE"]


class TrustedAccountCreateRequest(BaseModel):
    name: str
    data: dict
    provider: str
    secret_schema_id: str
    secret_data: dict
    schedule: Union[dict, None] = None
    sync_options: Union[dict, None] = None
    plugin_options: Union[dict, None] = None
    tags: Union[dict, None] = None
    resource_group: ResourceGroup
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountUpdateRequest(BaseModel):
    trusted_account_id: str
    name: Union[str, None] = None
    data: Union[dict, None] = None
    schedule: Union[dict, None] = None
    sync_options: Union[dict, None] = None
    plugin_options: Union[dict, None] = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountUpdateSecretRequest(BaseModel):
    trusted_account_id: str
    secret_schema_id: str
    secret_data: dict
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountDeleteRequest(BaseModel):
    trusted_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountSyncRequest(BaseModel):
    trusted_account_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class TrustedAccountGetRequest(BaseModel):
    trusted_account_id: str
    workspace_id: Union[str, list, None] = None
    domain_id: str


class TrustedAccountSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    trusted_account_id: Union[str, None] = None
    name: Union[str, None] = None
    provider: Union[str, None] = None
    secret_schema_id: Union[str, None] = None
    trusted_secret_id: Union[str, None] = None
    workspace_id: Union[str, list, None] = None
    domain_id: str


class TrustedAccountStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, list, None] = None
    domain_id: str
