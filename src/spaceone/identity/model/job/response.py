from datetime import datetime
from typing import Union, Literal, List
from pydantic import BaseModel

from spaceone.core import utils

__all__ = ["JobResponse", "JobsResponse"]

ResourceGroup = Literal["DOMAIN", "WORKSPACE"]
Status = Literal["PENDING", "IN_PROGRESS", "FAILURE", "SUCCESS", "CANCELD"]


class JobResponse(BaseModel):
    job_id: Union[str, None] = None
    status: Status
    resource_group: ResourceGroup
    trusted_account_id: Union[str, None] = None
    plugin_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    finished_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        return data


class JobsResponse(BaseModel):
    results: List[JobResponse] = []
    total_count: int
