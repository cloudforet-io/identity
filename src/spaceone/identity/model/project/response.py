from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.core import utils

from spaceone.identity.model.project.request import ProjectType

__all__ = ["ProjectResponse", "ProjectsResponse"]


class ProjectResponse(BaseModel):
    project_id: Union[str, None] = None
    name: Union[str, None] = None
    project_type: Union[ProjectType, None] = None
    tags: Union[dict, None] = {}
    users: Union[List[str], None] = None
    user_groups: Union[List[str], None] = None
    project_group_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        return data


class ProjectsResponse(BaseModel):
    results: List[ProjectResponse] = []
    total_count: int
