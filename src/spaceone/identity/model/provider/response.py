from datetime import datetime
from typing import Union, List
from pydantic import BaseModel
from spaceone.core import utils

__all__ = ["ProviderResponse", "ProvidersResponse"]


class ProviderResponse(BaseModel):
    provider: Union[str, None] = None
    name: Union[str, None] = None
    order: Union[int, None] = None
    template: Union[dict, None] = None
    metadata: Union[dict, None] = None
    capability: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['created_at'] = utils.datetime_to_iso8601(data['created_at'])
        return data


class ProvidersResponse(BaseModel):
    results: List[ProviderResponse] = []
    total_count: int
