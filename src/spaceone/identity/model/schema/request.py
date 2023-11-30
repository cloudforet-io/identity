from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "SchemaCreateRequest",
    "SchemaUpdateRequest",
    "SchemaDeleteRequest",
    "SchemaGetRequest",
    "SchemaSearchQueryRequest",
    "SchemaStatQueryRequest",
]

SchemaType = Literal["SERVICE_ACCOUNT", "TRUSTED_ACCOUNT", "SECRET", "TRUSTING_SECRET"]


class SchemaCreateRequest(BaseModel):
    schema_id: str
    name: str
    schema_type: SchemaType
    schema: dict
    provider: str
    related_schemas: Union[list, None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class SchemaUpdateRequest(BaseModel):
    schema_id: str
    name: Union[str, None] = None
    schema: Union[dict, None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class SchemaDeleteRequest(BaseModel):
    schema_id: str
    domain_id: str


class SchemaGetRequest(BaseModel):
    schema_id: str
    domain_id: str


class SchemaSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    schema_id: Union[str, None] = None
    name: Union[str, None] = None
    schema_type: Union[SchemaType, None] = None
    provider: Union[str, None] = None
    related_schema_id: Union[str, None] = None
    is_managed: Union[bool, None] = None
    domain_id: str


class SchemaStatQueryRequest(BaseModel):
    query: dict = None
    domain_id: str
