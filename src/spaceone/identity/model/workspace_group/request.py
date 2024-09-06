from typing import Dict, List, Literal, Union

from pydantic import BaseModel

__all__ = [
    "WorkspaceGroupCreateRequest",
    "WorkspaceGroupUpdateRequest",
    "WorkspaceGroupDeleteRequest",
    "WorkspaceGroupAddUsersRequest",
    "WorkspaceGroupRemoveUsersRequest",
    "WorkspaceGroupUpdateRoleRequest",
    "WorkspaceGroupGetRequest",
    "WorkspaceGroupSearchQueryRequest",
    "WorkspaceGroupStatQueryRequest",
    "State",
]

State = Literal["ENABLED", "DISABLED", "PENDING"]


class WorkspaceGroupCreateRequest(BaseModel):
    name: str
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupUpdateRequest(BaseModel):
    workspace_group_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupDeleteRequest(BaseModel):
    workspace_group_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupAddUsersRequest(BaseModel):
    workspace_group_id: str
    users: List[Dict[str, str]]
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupRemoveUsersRequest(BaseModel):
    workspace_group_id: str
    users: List[Dict[str, str]]
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupUpdateRoleRequest(BaseModel):
    workspace_group_id: str
    user_id: str
    role_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupGetRequest(BaseModel):
    workspace_group_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    workspace_group_id: Union[str, None] = None
    name: Union[str, None] = None
    created_by: Union[str, None] = None
    updated_by: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class WorkspaceGroupStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
