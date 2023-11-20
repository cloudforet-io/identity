from typing import Union, List
from pydantic import BaseModel

__all__ = ["APIKeyResponse", "APIKeysResponse"]


class APIKeyResponse(BaseModel):
    api_key_id: Union[str, None] = None
    api_key: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[str, None] = None
    user_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[str, None] = None
    last_accessed_at: Union[str, None] = None


class APIKeysResponse(BaseModel):
    results: List[APIKeyResponse]
    total_count: int
