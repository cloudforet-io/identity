from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "WorkspaceUserCreateRequest",
    "WorkspaceUserGetRequest",
    "WorkspaceUserSearchQueryRequest",
    "WorkspaceUserStatQueryRequest",
    "AuthType",
    "State",
]

State = Literal["ENABLED", "DISABLED", "PENDING"]
AuthType = Literal["LOCAL", "EXTERNAL"]
PermissionGroup = Literal["DOMAIN", "WORKSPACE"]


class WorkspaceUserCreateRequest(BaseModel):
    user_id: str
    password: Union[str, None] = None
    name: Union[str, None] = ""
    email: Union[str, None] = ""
    auth_type: AuthType
    language: Union[str, None] = None
    timezone: Union[str, None] = None
    tags: Union[dict, None] = None
    reset_password: Union[bool, None] = False
    domain_id: str
    workspace_id: str
    role_id: str


class WorkspaceUserGetRequest(BaseModel):
    user_id: str
    domain_id: str
    workspace_id: str


class WorkspaceUserSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    user_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    email: Union[str, None] = None
    auth_type: Union[AuthType, None] = None
    domain_id: str
    workspace_id: Union[str, None] = None


class WorkspaceUserStatQueryRequest(BaseModel):
    query: dict
    domain_id: str
    workspace_id: Union[str, None] = None
