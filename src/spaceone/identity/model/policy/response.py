from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

__all__ = ["PolicyResponse", "PoliciesResponse"]


class PolicyResponse(BaseModel):
    policy_id: Union[str, None]
    name: Union[str, None]
    permissions: Union[List[str], None]
    tags: Union[dict, None]
    is_managed: Union[bool, None]
    domain_id: Union[str, None]
    created_at: Union[datetime, None]


class PoliciesResponse(BaseModel):
    results: List[PolicyResponse]
    total_count: int
