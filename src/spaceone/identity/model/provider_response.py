from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

__all__ = ["ProviderResponse", "ProvidersResponse"]


class ProviderResponse(BaseModel):
    provider: Union[str, None] = None
    name: Union[str, None] = None
    order: Union[int, None] = None
    template: Union[dict, None] = None
    metadata: Union[dict, None] = None
    capability: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str
    created_at: Union[datetime, None] = None


class ProvidersResponse(BaseModel):
    results: List[ProviderResponse] = []
    total_count: int
