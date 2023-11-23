from datetime import datetime
from typing import Union, List
from pydantic import BaseModel
from spaceone.core import utils

from spaceone.identity.model.role.request import RoleType, PagePermissionType

__all__ = ["RoleResponse", "RolesResponse"]


class RoleResponse(BaseModel):
    role_id: Union[str, None] = None
    name: Union[str, None] = None
    role_type: Union[RoleType, None] = None
    policies: Union[List[str], None] = None
    page_permissions: Union[List[PagePermissionType], None] = None
    tags: Union[dict, None] = None
    is_managed: Union[bool, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['created_at'] = utils.datetime_to_iso8601(data['created_at'])
        return data


class RolesResponse(BaseModel):
    results: List[RoleResponse]
    total_count: int
