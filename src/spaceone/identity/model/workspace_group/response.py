from datetime import datetime
from typing import List, Union

from pydantic.main import BaseModel
from spaceone.core import utils

__all__ = ["WorkspaceGroupResponse", "WorkspaceGroupsResponse"]


class WorkspaceGroupUser(BaseModel):
    user_id: str
    role_id: str
    role_type: str
    user_name: Union[str, None] = None
    state: Union[str, None] = None


class WorkspaceGroupResponse(BaseModel):
    workspace_group_id: Union[str, None] = None
    name: Union[str, None] = None
    workspace_count: Union[int, None] = None
    users: Union[List[WorkspaceGroupUser], None] = None
    tags: Union[dict, None] = None
    created_by: Union[str, None] = None
    updated_by: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class WorkspaceGroupsResponse(BaseModel):
    results: List[WorkspaceGroupResponse]
    total_count: int
