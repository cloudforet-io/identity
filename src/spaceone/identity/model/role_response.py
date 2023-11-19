from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.identity.model.role_request import RoleType

__all__ = ["RoleResponse", "RolesResponse"]


class RoleResponse(BaseModel):
    role_id: Union[str, None] = None
    name: Union[str, None] = None
    role_type: Union[RoleType, None] = None
    policy_id: Union[str, None] = None
    permissions: Union[list, None] = None
    tags: Union[dict, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None


class RolesResponse(BaseModel):
    results: List[RoleResponse]
    total_count: int
