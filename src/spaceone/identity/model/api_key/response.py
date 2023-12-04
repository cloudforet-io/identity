from typing import Union, List
from pydantic import BaseModel

from datetime import datetime
from spaceone.core import utils

__all__ = ["APIKeyResponse", "APIKeysResponse"]


class APIKeyResponse(BaseModel):
    api_key_id: Union[str, None] = None
    api_key: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[str, None] = None
    user_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    last_accessed_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["last_accessed_at"] = utils.datetime_to_iso8601(data["last_accessed_at"])
        return data


class APIKeysResponse(BaseModel):
    results: List[APIKeyResponse]
    total_count: int
