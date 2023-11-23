from typing import Union, Literal
from pydantic import BaseModel

__all__ = ["AuthorizationVerifyRequest", "RoleType"]

Scope = Literal[
    "PUBLIC",
    "SYSTEM",
    "DOMAIN",
    "DOMAIN_READ",
    "WORKSPACE",
    "WORKSPACE_READ",
    "DOMAIN_OR_WORKSPACE",
    "DOMAIN_OR_WORKSPACE_READ",
    "PROJECT",
    "PROJECT_READ",
    "DOMAIN_OR_USER",
    "DOMAIN_OR_USER_READ",
    "USER",
]

RoleType = Literal[
    "SYSTEM_ADMIN", "DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "NO_ROLE"
]


class AuthorizationVerifyRequest(BaseModel):
    service: str
    resource: str
    verb: str
    scope: Scope
    request_user_id: Union[str, None] = None
    request_project_id: Union[str, None] = None
    request_workspace_id: Union[str, None] = None
    request_domain_id: Union[str, None] = None
    require_user_id: Union[bool, None] = None
    require_project_id: Union[bool, None] = None
    require_workspace_id: Union[bool, None] = None
    require_domain_id: Union[bool, None] = None
    user_id: str
    domain_id: str
