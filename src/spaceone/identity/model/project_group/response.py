from datetime import datetime
from typing import Union, List
from pydantic import BaseModel
from spaceone.core import utils

__all__ = ["ProjectGroupResponse", "ProjectGroupsResponse"]


class ProjectGroupResponse(BaseModel):
    project_group_id: Union[str, None] = None
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    users: Union[List[str], None] = None
    reference_id: Union[str, None] = None
    is_managed: Union[bool, None] = None
    trusted_account_id: Union[str, None] = None
    parent_group_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    last_synced_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["last_synced_at"] = utils.datetime_to_iso8601(data.get("last_synced_at"))
        return data


class ProjectGroupsResponse(BaseModel):
    results: List[ProjectGroupResponse] = []
    total_count: int
