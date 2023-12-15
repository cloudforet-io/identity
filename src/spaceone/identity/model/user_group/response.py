from datetime import datetime
from typing import Union, List
from pydantic import BaseModel
from spaceone.core import utils

__all__ = ["UserGroupResponse", "UserGroupsResponse"]


class UserGroupResponse(BaseModel):
    user_group_id: Union[str, None] = None
    name: Union[str, None] = None
    users: Union[List[str], None] = None
    tags: Union[dict, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        return data


class UserGroupsResponse(BaseModel):
    results: List[UserGroupResponse]
    total_count: int
