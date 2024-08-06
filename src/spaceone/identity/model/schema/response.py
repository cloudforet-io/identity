from datetime import datetime
from typing import Union, List
from pydantic import BaseModel, Field
from spaceone.core import utils
from spaceone.identity.model.schema.request import SchemaType

__all__ = ["SchemaResponse", "SchemasResponse"]


class SchemaResponse(BaseModel):
    schema_id: Union[str, None] = None
    name: Union[str, None] = None
    schema_type: Union[SchemaType, None] = None
    data_schema: Union[dict, None] = Field(None, alias="schema")
    provider: Union[str, None] = None
    related_schemas: Union[List[str], None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    is_managed: Union[bool, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)

        if "data_schema" in data:
            data["schema"] = data["data_schema"]
            del data["data_schema"]

        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class SchemasResponse(BaseModel):
    results: List[SchemaResponse] = []
    total_count: int
