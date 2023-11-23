from typing import Union
from pydantic import BaseModel

__all__ = [
    "ProviderCreateRequest",
    "ProviderUpdateRequest",
    "ProviderDeleteRequest",
    "ProviderGetRequest",
    "ProviderSearchQueryRequest",
    "ProviderStatQueryRequest",
]


class ProviderCreateRequest(BaseModel):
    provider: str
    name: str
    order: Union[int, None] = None
    template: Union[dict, None] = None
    metadata: Union[dict, None] = None
    capability: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class ProviderUpdateRequest(BaseModel):
    provider: str
    name: Union[str, None] = None
    order: Union[int, None] = None
    template: Union[dict, None] = None
    metadata: Union[dict, None] = None
    capability: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class ProviderDeleteRequest(BaseModel):
    provider: str
    domain_id: str


class ProviderGetRequest(BaseModel):
    provider: str
    domain_id: str


class ProviderSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    provider: Union[str, None] = None
    name: Union[str, None] = None
    domain_id: str


class ProviderStatQueryRequest(BaseModel):
    query: dict = None
    domain_id: str
