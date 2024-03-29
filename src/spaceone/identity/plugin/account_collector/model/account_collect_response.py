from typing import Union, List
from pydantic import BaseModel, Field

__all__ = ["PluginResponse", "AccountsResponse"]


class PluginResponse(BaseModel):
    metadata: dict


class AccountResponse(BaseModel):
    name: Union[str, None] = None
    resource_id: Union[str, None] = None
    data: Union[dict, None] = None
    secret_schema_id: Union[str, None] = None
    secret_data: Union[dict, None] = None
    tags: Union[dict, None] = None
    location: Union[list, None] = None


class AccountsResponse(BaseModel):
    results: List[AccountResponse] = None
