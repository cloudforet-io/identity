from typing import Union, Literal, List
from pydantic import BaseModel, Field

__all__ = [
    "SchemaCreateRequest",
    "SchemaUpdateRequest",
    "SchemaDeleteRequest",
    "SchemaGetRequest",
    "SchemaSearchQueryRequest",
    "SchemaStatQueryRequest",
    "SchemaType",
]

SchemaType = Literal["SERVICE_ACCOUNT", "TRUSTED_ACCOUNT", "SECRET", "TRUSTING_SECRET"]


class SchemaCreateRequest(BaseModel):
    schema_id: str
    name: str
    schema_type: SchemaType
    data_schema: Union[dict, None] = Field(None, alias="schema")
    provider: str
    related_schemas: Union[List[str], None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class SchemaUpdateRequest(BaseModel):
    schema_id: str
    name: Union[str, None] = None
    data_schema: Union[dict, None] = Field(None, alias="schema")
    related_schemas: Union[List[str], None] = None
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
