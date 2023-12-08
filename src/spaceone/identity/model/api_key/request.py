from datetime import datetime
from typing import Union
from pydantic import BaseModel

__all__ = [
    "APIKeyCreateRequest",
    "APIKeyUpdateRequest",
    "APIKeyDeleteRequest",
    "APIKeyGetRequest",
    "APIKeySearchQueryRequest",
    "APIKeyEnableRequest",
    "APIKeyDisableRequest",
    "APIKeyStatQueryRequest",
]


class APIKeyCreateRequest(BaseModel):
    user_id: str
    name: Union[str, None] = None
    expired_at: Union[str, None] = None
    domain_id: str


class APIKeyUpdateRequest(BaseModel):
    api_key_id: str
    name: Union[str, None] = None
    domain_id: str
    user_id: Union[str, None] = None


class APIKeyEnableRequest(BaseModel):
    api_key_id: str
    domain_id: str
    user_id: Union[str, None] = None


class APIKeyDisableRequest(BaseModel):
    api_key_id: str
    domain_id: str
    user_id: Union[str, None] = None


class APIKeyDeleteRequest(BaseModel):
    api_key_id: str
    domain_id: str
    user_id: Union[str, None] = None


class APIKeyGetRequest(BaseModel):
    api_key_id: str
    domain_id: str
    user_id: Union[str, None] = None


class APIKeySearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    api_key_id: Union[str, None] = None
    name: Union[str, None] = None
    user_id: Union[str, None] = None
    state: Union[str, None] = None
    domain_id: str


class APIKeyStatQueryRequest(BaseModel):
    query: dict
    domain_id: str
    user_id: Union[str, None] = None
