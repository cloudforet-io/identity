from datetime import datetime
from typing import Union, List
from pydantic import BaseModel
from spaceone.core import utils

__all__ = ["PackageResponse", "PackagesResponse"]


class PackageResponse(BaseModel):
    package_id: Union[str, None] = None
    name: Union[str, None] = None
    description: Union[str, None] = None
    order: Union[int, None] = None
    is_default: Union[bool, None] = None
    tags: Union[dict, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class PackagesResponse(BaseModel):
    results: List[PackageResponse]
    total_count: int
