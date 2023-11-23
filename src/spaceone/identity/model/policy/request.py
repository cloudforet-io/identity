from typing import Union, List
from pydantic import BaseModel

__all__ = [
    "PolicyCreateRequest",
    "PolicyUpdateRequest",
    "PolicyDeleteRequest",
    "PolicyGetRequest",
    "PolicySearchQueryRequest",
    "PolicyStatQueryRequest",
]


class PolicyCreateRequest(BaseModel):
    name: str
    permissions: List[str]
    tags: Union[dict, None] = None
    domain_id: str


class PolicyUpdateRequest(BaseModel):
    policy_id: str
    name: Union[str, None] = None
    permissions: Union[List[str], None] = None
    tags: Union[dict, None] = None
    domain_id: str


class PolicyDeleteRequest(BaseModel):
    policy_id: str
    domain_id: str


class PolicyGetRequest(BaseModel):
    policy_id: str
    domain_id: str


class PolicySearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    policy_id: Union[str, None] = None
    name: Union[str, None] = None
    domain_id: str


class PolicyStatQueryRequest(BaseModel):
    query: Union[dict, None] = None
    domain_id: str
