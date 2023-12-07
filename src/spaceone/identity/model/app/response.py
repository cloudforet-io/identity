from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.core import utils

from spaceone.identity.model.app.request import State, PermissionGroup, RoleType

__all__ = ["AppResponse", "AppsResponse"]


class AppResponse(BaseModel):
    app_id: Union[str, None] = None
    api_key: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    role_type: Union[RoleType, None] = None
    api_key_id: Union[str, None] = None
    role_id: Union[str, None] = None
    permission_group: Union[PermissionGroup, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    last_accessed_at: Union[datetime, None] = None
    expired_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["last_accessed_at"] = utils.datetime_to_iso8601(data["last_accessed_at"])
        data["expired_at"] = utils.datetime_to_iso8601(data["expired_at"])
        return data


class AppsResponse(BaseModel):
    results: List[AppResponse]
    total_count: int
