from datetime import datetime
from typing import List, Union, Literal
from pydantic import BaseModel

from spaceone.core import utils

from spaceone.identity.model.domain.request import State

__all__ = [
    "DomainResponse",
    "DomainsResponse",
    "DomainAuthInfoResponse",
    "DomainSecretResponse",
]

ExternalAuthState = Literal["ENABLED", "DISABLED"]


class DomainResponse(BaseModel):
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    tags: Union[dict, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        return data


class DomainAuthInfoResponse(BaseModel):
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    external_auth_state: Union[ExternalAuthState, None] = None
    metadata: Union[dict, None] = None
    config: Union[dict, None] = None


class DomainSecretResponse(BaseModel):
    domain_id: Union[str, None] = None
    public_key: Union[str, None] = None


class DomainsResponse(BaseModel):
    results: List[DomainResponse]
    total_count: int
