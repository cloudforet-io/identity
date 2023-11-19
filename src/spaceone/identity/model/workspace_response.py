from datetime import datetime
from typing import Union, List, Literal
from enum import Enum
from pydantic import BaseModel

__all__ = ["WorkspaceResponse", "WorkspacesResponse"]

State = Literal["ENABLED", "DISABLED"]


class WorkspaceResponse(BaseModel):
    workspace_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    tags: Union[dict, None] = {}
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None


class WorkspacesResponse(BaseModel):
    results: List[WorkspaceResponse]
    total_count: int
