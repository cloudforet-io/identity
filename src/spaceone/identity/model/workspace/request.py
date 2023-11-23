from typing import Union
from pydantic import BaseModel

__all__ = [
    "WorkspaceCreateRequest",
    "WorkspaceUpdateRequest",
    "WorkspaceDeleteRequest",
    "WorkspaceEnableRequest",
    "WorkspaceDisableRequest",
    "WorkspaceGetRequest",
    "WorkspaceSearchQueryRequest",
    "WorkspaceStatQueryRequest",
]


class WorkspaceCreateRequest(BaseModel):
    name: str
    tags: dict
    domain_id: str


class WorkspaceUpdateRequest(BaseModel):
    workspace_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class WorkspaceDeleteRequest(BaseModel):
    workspace_id: str
    domain_id: str


class WorkspaceEnableRequest(BaseModel):
    workspace_id: str
    domain_id: str


class WorkspaceDisableRequest(BaseModel):
    workspace_id: str
    domain_id: str


class WorkspaceGetRequest(BaseModel):
    workspace_id: str
    domain_id: str


class WorkspaceSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    name: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceStatQueryRequest(BaseModel):
    query: dict
    domain_id: str
