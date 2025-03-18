from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "ServiceAccountCreateRequest",
    "ServiceAccountUpdateRequest",
    "ServiceAccountUpdateSecretRequest",
    "ServiceAccountDeleteSecretRequest",
    "ServiceAccountDeleteRequest",
    "ServiceAccountGetRequest",
    "ServiceAccountSearchQueryRequest",
    "ServiceAccountStatQueryRequest",
    "ServiceAccountAnalyzeQueryRequest",
    "State",
]

State = Literal["PENDING", "ACTIVE", "INACTIVE", "DELETED"]


class ServiceAccountCreateRequest(BaseModel):
    name: str
    data: dict
    provider: str
    secret_schema_id: Union[str, None] = None
    secret_data: Union[dict, None] = None
    tags: Union[dict, None] = None
    service_account_mgr_id: Union[str, None] = None
    trusted_account_id: Union[str, None] = None
    project_id: str
    workspace_id: str
    domain_id: str


class ServiceAccountUpdateRequest(BaseModel):
    service_account_id: str
    name: Union[str, None] = None
    data: Union[dict, None] = None
    tags: Union[dict, None] = None
    service_account_mgr_id: Union[str, None] = None
    project_id: Union[str, None] = None
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountUpdateSecretRequest(BaseModel):
    service_account_id: str
    secret_schema_id: str
    secret_data: dict
    trusted_account_id: Union[str, None] = None
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountDeleteSecretRequest(BaseModel):
    service_account_id: str
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
    state: Union[State, None] = None
    provider: Union[str, None] = None
    secret_schema_id: Union[str, None] = None
    secret_id: Union[str, None] = None
    trusted_account_id: Union[str, None] = None
    project_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountAnalyzeQueryRequest(BaseModel):
    query: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str
    user_projects: Union[list, None] = None


class ServiceAccountStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
    user_projects: Union[list, None] = None
