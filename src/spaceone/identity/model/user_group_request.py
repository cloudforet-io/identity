from typing import Union, List
from pydantic import BaseModel

__all__ = [
    "UserGroupCreateRequest",
    "UserGroupUpdateRequest",
    "UserGroupDeleteRequest",
    "UserGroupAddUsersRequest",
    "UserGroupRemoveUsersRequest",
    "UserGroupGetRequest",
    "UserGroupSearchQueryRequest",
    "UserGroupStatQueryRequest",
]


class UserGroupCreateRequest(BaseModel):
    name: str
    tags: Union[dict, None] = None
    workspace_id: str
    domain_id: str


class UserGroupUpdateRequest(BaseModel):
    user_group_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    workspace_id: str
    domain_id: str


class UserGroupDeleteRequest(BaseModel):
    user_group_id: str
    workspace_id: str
    domain_id: str


class UserGroupAddUsersRequest(BaseModel):
    user_group_id: str
    users: List[str]
    workspace_id: str
    domain_id: str


class UserGroupRemoveUsersRequest(BaseModel):
    user_group_id: str
    users: List[str]
    workspace_id: str
    domain_id: str


class UserGroupGetRequest(BaseModel):
    user_group_id: str
    workspace_id: str
    domain_id: str


class UserGroupSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    user_group_id: Union[str, None] = None
    name: Union[str, None] = None
    user_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class UserGroupStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
