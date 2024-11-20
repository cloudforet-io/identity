from typing import Union, List
from pydantic import BaseModel

__all__ = [
    "PackageCreateRequest",
    "PackageUpdateRequest",
    "PackageDeleteRequest",
    "PackageSetDefaultRequest",
    "PackageChangeOrderRequest",
    "PackageGetRequest",
    "PackageSearchQueryRequest",
    "PackageStatQueryRequest",
]


class PackageCreateRequest(BaseModel):
    name: str
    description: Union[str, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class PackageUpdateRequest(BaseModel):
    package_id: str
    name: Union[str, None] = None
    description: Union[str, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class PackageDeleteRequest(BaseModel):
    package_id: str
    domain_id: str


class PackageSetDefaultRequest(BaseModel):
    package_id: str
    domain_id: str


class PackageChangeOrderRequest(BaseModel):
    package_id: str
    order: int
    domain_id: str


class PackageGetRequest(BaseModel):
    package_id: str
    domain_id: str


class PackageSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    package_id: Union[str, None] = None
    name: Union[str, None] = None
    domain_id: str


class PackageStatQueryRequest(BaseModel):
    query: dict
    domain_id: str
