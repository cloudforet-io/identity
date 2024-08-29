from datetime import datetime
from typing import List, Union

from pydantic import BaseModel
from spaceone.core import utils

from spaceone.identity.model.role.request import RoleType, State

__all__ = ["RoleResponse", "RolesResponse", "BasicRoleResponse", "BasicRolesResponse"]


class RoleResponse(BaseModel):
    role_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    role_type: Union[RoleType, None] = None
    permissions: Union[List[str], None] = None
    page_access: Union[List[str], None] = None
    tags: Union[dict, None] = None
    is_managed: Union[bool, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class RolesResponse(BaseModel):
    results: List[RoleResponse]
    total_count: int


class BasicRoleResponse(BaseModel):
    role_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    role_type: Union[RoleType, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class BasicRolesResponse(BaseModel):
    results: List[BasicRoleResponse]
    total_count: int
