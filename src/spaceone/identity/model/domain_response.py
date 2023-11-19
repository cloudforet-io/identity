from typing import List, Union, Literal
from pydantic import BaseModel, validator, Extra

from spaceone.core.utils import datetime_to_iso8601

from spaceone.identity.model.domain_request import State

__all__ = [
    "DomainResponse",
    "DomainsResponse",
    "DomainMetadataResponse",
    "DomainSecretResponse",
]

ExternalAuthState = Literal["ENABLED", "DISABLED"]


class DomainResponse(BaseModel, extra=Extra.ignore, orm_mode=True):
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    tags: Union[dict, None] = {}
    created_at: Union[str, None] = None

    _convert_datetime = validator("created_at", pre=True, allow_reuse=True)(
        datetime_to_iso8601
    )


class DomainMetadataResponse(BaseModel, orm_mode=True):
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    external_auth_state: ExternalAuthState
    metadata_info: Union[dict, None] = None


class DomainSecretResponse(BaseModel, orm_mode=True):
    domain_id: Union[str, None] = None
    key: Union[str, None] = None
    key_type: Union[str, None] = None


class DomainsResponse(BaseModel, orm_mode=True):
    results: List[DomainResponse]
    total_count: int
