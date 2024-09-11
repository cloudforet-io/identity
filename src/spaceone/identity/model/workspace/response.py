from datetime import datetime
from typing import List, Union

from pydantic import BaseModel
from spaceone.core import utils

from spaceone.identity.model.workspace.request import State

__all__ = ["WorkspaceResponse", "WorkspacesResponse"]


class WorkspaceResponse(BaseModel):
    workspace_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    tags: Union[dict, None] = None
    created_by: Union[str, None] = None
    references: Union[list, None] = None
    is_managed: Union[bool, None] = None
    is_dormant: Union[bool, None] = None
    dormant_ttl: Union[int, None] = None
    service_account_count: Union[int, None] = None
    user_count: Union[int, None] = None
    cost_info: Union[dict, None] = None
    trusted_account_id: Union[str, None] = None
    workspace_group_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    last_synced_at: Union[datetime, None] = None
    dormant_updated_at: Union[datetime, None] = None
    changed_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["last_synced_at"] = utils.datetime_to_iso8601(data.get("last_synced_at"))
        data["dormant_updated_at"] = utils.datetime_to_iso8601(
            data.get("dormant_updated_at")
        )
        data["changed_at"] = utils.datetime_to_iso8601(data.get("changed_at"))
        return data


class WorkspacesResponse(BaseModel):
    results: List[WorkspaceResponse]
    total_count: int
