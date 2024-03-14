from typing import Union, Literal, List
from pydantic import BaseModel

__all__ = [
    "ProjectGroupCreateRequest",
    "ProjectGroupUpdateRequest",
    "ProjectChangeParentGroupRequest",
    "ProjectGroupDeleteRequest",
    "ProjectGroupAddUsersRequest",
    "ProjectGroupRemoveUsersRequest",
    "ProjectGroupGetRequest",
    "ProjectGroupSearchQueryRequest",
    "ProjectGroupStatQueryRequest",
]


class ProjectGroupCreateRequest(BaseModel):
    name: str
    tags: Union[dict, None] = {}
    parent_group_id: Union[str, None] = None
    workspace_id: str
    domain_id: str


class ProjectGroupUpdateRequest(BaseModel):
    project_group_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    workspace_id: str
    domain_id: str


class ProjectChangeParentGroupRequest(BaseModel):
    project_group_id: str
    parent_group_id: Union[str, None] = None
    workspace_id: str
    domain_id: str


class ProjectGroupDeleteRequest(BaseModel):
    project_group_id: str
    workspace_id: str
    domain_id: str


class ProjectGroupAddUsersRequest(BaseModel):
    project_group_id: str
    users: List[str]
    workspace_id: str
    domain_id: str


class ProjectGroupRemoveUsersRequest(BaseModel):
    project_group_id: str
    users: List[str]
    workspace_id: str
    domain_id: str


class ProjectGroupGetRequest(BaseModel):
    project_group_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class ProjectGroupSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    project_group_id: Union[str, None] = None
    name: Union[str, None] = None
    parent_group_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class ProjectGroupStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
