from typing import Dict, List, Literal, Union

from pydantic import BaseModel

__all__ = [
    "WorkspaceGroupDetailsUpdateRequest",
    "WorkspaceGroupDetailsDeleteRequest",
    "WorkspaceGroupDetailsAddWorkspacesRequest",
    "WorkspaceGroupDetailsRemoveWorkspacesRequest",
    "WorkspaceGroupDetailsFindRequest",
    "WorkspaceGroupDetailsAddUsersRequest",
    "WorkspaceGroupDetailsRemoveUsersRequest",
    "WorkspaceGroupDetailsGetWorkspaceGroupsRequest",
]

State = Literal["ENABLED", "DISABLED", "PENDING"]


class WorkspaceGroupDetailsUpdateRequest(BaseModel):
    workspace_group_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    user_id: str
    domain_id: str


class WorkspaceGroupDetailsDeleteRequest(BaseModel):
    workspace_group_id: str
    user_id: str
    domain_id: str


class WorkspaceGroupDetailsAddWorkspacesRequest(BaseModel):
    workspace_group_id: str
    workspaces: List[str]
    user_id: str
    domain_id: str


class WorkspaceGroupDetailsRemoveWorkspacesRequest(BaseModel):
    workspace_group_id: str
    workspaces: List[str]
    user_id: str
    domain_id: str


class WorkspaceGroupDetailsFindRequest(BaseModel):
    workspace_group_id: str
    keyword: Union[str, None] = None
    state: Union[State, None] = None
    page: Union[dict, None] = None
    user_id: str
    domain_id: str


class WorkspaceGroupDetailsAddUsersRequest(BaseModel):
    workspace_group_id: str
    users: List[Dict[str, str]]
    user_id: str
    domain_id: str


class WorkspaceGroupDetailsRemoveUsersRequest(BaseModel):
    workspace_group_id: str
    users: List[str]
    user_id: str
    domain_id: str


class WorkspaceGroupDetailsGetWorkspaceGroupsRequest(BaseModel):
    # workspace_group_id: str
    user_id: str
    domain_id: str
