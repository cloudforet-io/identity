from datetime import datetime
from typing import List, Union, Literal
from pydantic import BaseModel

from spaceone.identity.model.domain_request import State

__all__ = [
    "DomainResponse",
    "DomainsResponse",
    "DomainMetadataResponse",
    "DomainSecretResponse",
]

ExternalAuthState = Literal["ENABLED", "DISABLED"]


class DomainResponse(BaseModel):
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    tags: Union[dict, None] = {}
    created_at: Union[datetime, None] = None


class DomainMetadataResponse(BaseModel):
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    external_auth_state: ExternalAuthState
    metadata_info: Union[dict, None] = None


class DomainSecretResponse(BaseModel):
    domain_id: Union[str, None] = None
    key: Union[str, None] = None
    key_type: Union[str, None] = None


class DomainsResponse(BaseModel):
    results: List[DomainResponse]
    total_count: int
