from datetime import datetime
from typing import Union, Literal
from pydantic import BaseModel, Field

__all__ = ["ExternalAuthResponse"]

State = Literal["ENABLED", "DISABLED"]


class Plugin(BaseModel):
    plugin_id: str
    version: Union[str, None] = None
    upgrade_mode: Union[str, None] = None
    options: Union[dict, None] = None
    schema_name: Union[str, None] = Field(None, alias="schema")
    metadata: dict
    secret_id: Union[dict, None] = None


class ExternalAuthResponse(BaseModel):
    domain_id: Union[str, None] = None
    state: Union[State, None] = None
    plugin_info: Union[Plugin, None] = None
    updated_at: Union[datetime, None] = None
