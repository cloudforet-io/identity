from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.core import utils

from spaceone.identity.model.app.request import State, ResourceGroup, RoleType

__all__ = ["CheckAppResponse", "AppResponse", "AppsResponse"]


class CheckAppResponse(BaseModel):
    permissions: List[str]
    projects: Union[List[str], None] = None


class AppResponse(BaseModel):
    app_id: Union[str, None] = None
    client_secret: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    tags: Union[dict, None] = None
    is_managed: Union[bool, None] = None
    role_type: Union[RoleType, None] = None
    client_id: Union[str, None] = None
    role_id: Union[str, None] = None
    resource_group: Union[ResourceGroup, None] = None
    project_id: Union[str, None] = None
    project_group_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    expired_at: Union[datetime, None] = None
    last_accessed_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["expired_at"] = utils.datetime_to_iso8601(data["expired_at"])
        data["last_accessed_at"] = utils.datetime_to_iso8601(
            data.get("last_accessed_at")
        )
        return data


class AppsResponse(BaseModel):
    results: List[AppResponse]
    total_count: int
