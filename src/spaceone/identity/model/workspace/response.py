from datetime import datetime
from typing import Union, List, Literal
from pydantic import BaseModel

from spaceone.core import utils

__all__ = ["WorkspaceResponse", "WorkspacesResponse"]

State = Literal["ENABLED", "DISABLED"]


class WorkspaceResponse(BaseModel):
    workspace_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    tags: Union[dict, None] = None
    created_by: Union[str, None] = None
    references: Union[list, None] = None
    is_managed: Union[bool, None] = None
    trusted_account_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    last_synced_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["last_synced_at"] = utils.datetime_to_iso8601(data.get("last_synced_at"))
        return data


class WorkspacesResponse(BaseModel):
    results: List[WorkspaceResponse]
    total_count: int
