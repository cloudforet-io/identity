from typing import Union, Literal, List
from pydantic import BaseModel

__all__ = [
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    "ProjectUpdateProjectTypeRequest",
    "ProjectDeleteRequest",
    "ProjectAddUsersRequest",
    "ProjectRemoveUsersRequest",
    "ProjectAddUserGroupsRequest",
    "ProjectRemoveUserGroupsRequest",
    "ProjectGetRequest",
    "ProjectSearchQueryRequest",
    "ProjectStatQueryRequest",
    "ProjectChangeProjectGroupRequest",
    "ProjectType",
]

ProjectType = Literal["PRIVATE", "PUBLIC"]


class ProjectCreateRequest(BaseModel):
    name: str
    project_type: ProjectType
    tags: Union[dict, None] = {}
    project_group_id: Union[str, None] = None
    workspace_id: str
    domain_id: str


class ProjectUpdateRequest(BaseModel):
    project_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    workspace_id: str
    domain_id: str


class ProjectUpdateProjectTypeRequest(BaseModel):
    project_id: str
    project_type: ProjectType
    workspace_id: str
    domain_id: str


class ProjectChangeProjectGroupRequest(BaseModel):
    project_id: str
    project_group_id: str
    workspace_id: str
    domain_id: str


class ProjectDeleteRequest(BaseModel):
    project_id: str
    workspace_id: str
    domain_id: str


class ProjectAddUsersRequest(BaseModel):
    project_id: str
    users: List[str]
    workspace_id: str
    domain_id: str


class ProjectRemoveUsersRequest(BaseModel):
    project_id: str
    users: List[str]
    workspace_id: str
    domain_id: str


class ProjectAddUserGroupsRequest(BaseModel):
    project_id: str
    user_groups: List[str]
    workspace_id: str
    domain_id: str


class ProjectRemoveUserGroupsRequest(BaseModel):
    project_id: str
    user_groups: List[str]
    workspace_id: str
    domain_id: str


class ProjectGetRequest(BaseModel):
    project_id: str
    workspace_id: str
    domain_id: str


class ProjectSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    project_id: Union[str, None] = None
    name: Union[str, None] = None
    user_id: Union[str, None] = None
    user_group_id: Union[str, None] = None
    project_group_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class ProjectStatQueryRequest(BaseModel):
    query: dict
    project_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str
