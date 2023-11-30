from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "DomainCreateRequest",
    "DomainUpdateRequest",
    "DomainDeleteRequest",
    "DomainEnableRequest",
    "DomainDisableRequest",
    "DomainGetRequest",
    "DomainGetAuthInfoRequest",
    "DomainGetPublicKeyRequest",
    "DomainSearchQueryRequest",
    "DomainStatQueryRequest",
    "State",
]

State = Literal["ENABLED", "DISABLED"]


class DomainCreateRequest(BaseModel):
    name: str
    admin: dict
    tags: Union[dict, None] = None


class DomainUpdateRequest(BaseModel):
    domain_id: str
    name: Union[str, None] = None
    tags: Union[dict, None] = None


class DomainDeleteRequest(BaseModel):
    domain_id: str


class DomainEnableRequest(BaseModel):
    domain_id: str


class DomainDisableRequest(BaseModel):
    domain_id: str


class DomainGetRequest(BaseModel):
    domain_id: str


class DomainGetAuthInfoRequest(BaseModel):
    name: str


class DomainGetPublicKeyRequest(BaseModel):
    domain_id: str


class DomainSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    domain_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None


class DomainStatQueryRequest(BaseModel):
    query: dict
