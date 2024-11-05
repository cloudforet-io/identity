from typing import Dict, List, Literal, Union

from pydantic import BaseModel

__all__ = [
    "WorkspaceGroupUserAddRequest",
    "WorkspaceGroupUserRemoveRequest",
    "WorkspaceGroupUserUpdateRoleRequest",
    "WorkspaceGroupUserFindRequest",
    "WorkspaceGroupUserGetRequest",
    "WorkspaceGroupUserSearchQueryRequest",
    "WorkspaceGroupUserStatQueryRequest",
]

State = Literal["ENABLED", "DISABLED", "PENDING"]


class WorkspaceGroupUserAddRequest(BaseModel):
    workspace_group_id: str
    users: List[Dict[str, str]]
    user_id: str
    domain_id: str


class WorkspaceGroupUserRemoveRequest(BaseModel):
    workspace_group_id: str
    users: List[Dict[str, str]]
    user_id: str
    domain_id: str


class WorkspaceGroupUserUpdateRoleRequest(BaseModel):
    workspace_group_id: str
    role_id: str
    target_user_id: str
    user_id: str
    domain_id: str


class WorkspaceGroupUserFindRequest(BaseModel):
    workspace_group_id: str
    keyword: Union[str, None] = None
    state: Union[State, None] = None
    page: Union[dict, None] = None
    user_id: str
    domain_id: str


class WorkspaceGroupUserGetRequest(BaseModel):
    workspace_group_id: str
    user_id: str
    domain_id: str


class WorkspaceGroupUserSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    workspace_group_id: Union[str, None] = None
    name: Union[str, None] = None
    created_by: Union[str, None] = None
    updated_by: Union[str, None] = None
    user_id: str
    domain_id: str


class WorkspaceGroupUserStatQueryRequest(BaseModel):
    query: dict
    workspace_group_id: str
    user_id: str
    domain_id: str
