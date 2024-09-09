from typing import List

from pydantic.main import BaseModel

__all__ = [
    "WorkspaceGroupUserSummaryResponse",
    "WorkspaceGroupUsersSummaryResponse",
]

from spaceone.identity.model.workspace_group.request import State


class WorkspaceGroupUserSummaryResponse(BaseModel):
    user_id: str
    name: str
    state: State


class WorkspaceGroupUsersSummaryResponse(BaseModel):
    results: List[WorkspaceGroupUserSummaryResponse]
    total_count: int
