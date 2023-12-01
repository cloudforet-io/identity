from typing import Union, List, Literal
from pydantic import BaseModel

__all__ = [
    "RoleCreateRequest",
    "RoleUpdateRequest",
    "RoleDeleteRequest",
    "RoleGetRequest",
    "RoleSearchQueryRequest",
    "RoleStatQueryRequest",
    'RoleType',
    'PagePermission',
]

RoleType = Literal["SYSTEM", "SYSTEM_ADMIN", "DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"]
PagePermissionType = Literal["VIEW", "MANAGE"]


class PagePermission(BaseModel):
    page: str
    permission: PagePermissionType


class RoleCreateRequest(BaseModel):
    name: str
    role_type: RoleType
    api_permissions: Union[List[str], None] = None
    page_permissions: Union[List[PagePermission], None] = None
    tags: Union[dict, None] = None
    domain_id: str


class RoleUpdateRequest(BaseModel):
    role_id: str
    name: Union[str, None] = None
    api_permissions: Union[List[str], None] = None
    page_permissions: Union[List[PagePermission], None] = None
    tags: Union[dict, None]
    domain_id: str


class RoleDeleteRequest(BaseModel):
    role_id: str
    domain_id: str


class RoleGetRequest(BaseModel):
    role_id: str
    domain_id: str


class RoleSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    role_id: Union[str, None] = None
    name: Union[str, None] = None
    role_type: Union[RoleType, None] = None
    domain_id: str


class RoleStatQueryRequest(BaseModel):
    query: dict
    domain_id: str
