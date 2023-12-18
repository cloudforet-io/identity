from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "RoleBindingCreateRequest",
    "RoleBindingUpdateRoleRequest",
    "RoleBindingDeleteRequest",
    "RoleBindingGetRequest",
    "RoleBindingSearchQueryRequest",
    "RoleBindingStatQueryRequest",
    "ResourceGroup",
]

ResourceGroup = Literal["DOMAIN", "WORKSPACE"]


class RoleBindingCreateRequest(BaseModel):
    user_id: str
    role_id: str
    resource_group: ResourceGroup
    workspace_id: Union[str, None] = None
    domain_id: str


class RoleBindingUpdateRoleRequest(BaseModel):
    role_binding_id: str
    role_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class RoleBindingDeleteRequest(BaseModel):
    role_binding_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class RoleBindingGetRequest(BaseModel):
    role_binding_id: str
    workspace_id: Union[str, None] = None
    domain_id: str


class RoleBindingSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    role_binding_id: Union[str, None] = None
    role_type: Union[str, None] = None
    user_id: Union[str, None] = None
    role_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str


class RoleBindingStatQueryRequest(BaseModel):
    query: dict
    workspace_id: Union[str, None] = None
    domain_id: str
