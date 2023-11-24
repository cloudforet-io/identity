from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

__all__ = ["ProjectGroupResponse", "ProjectGroupsResponse"]


class ProjectGroupResponse(BaseModel):
    project_group_id: Union[str, None] = None
    name: Union[str, None] = None
    tags: Union[dict, None] = None
    parent_group_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None


class ProjectGroupsResponse(BaseModel):
    results: List[ProjectGroupResponse] = []
    total_count: int
