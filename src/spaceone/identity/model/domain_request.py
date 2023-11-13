from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "DomainCreateRequest",
    "DomainUpdateRequest",
    "DomainRequest",
    "DomainGetMetadataRequest",
    "DomainSearchQueryRequest",
    "DomainStatQuery",
    "State",
]

State = Literal["ENABLED", "DISABLED"]


class DomainCreateRequest(BaseModel):
    name: str
    admin: dict
    tags: Union[dict, None] = {}


class DomainUpdateRequest(BaseModel):
    domain_id: str
    tags: Union[dict, None] = {}


class DomainRequest(BaseModel):
    domain_id: str


class DomainGetMetadataRequest(BaseModel):
    name: str


class DomainSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None


class DomainStatQuery(BaseModel):
    query: dict
