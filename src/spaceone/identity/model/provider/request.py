from typing import Union, Literal
from pydantic import BaseModel

__all__ = [
    "UpgradeMode",
    "Plugin",
    "ProviderCreateRequest",
    "ProviderUpdateRequest",
    "ProviderUpdatePluginRequest",
    "ProviderDeleteRequest",
    "ProviderGetRequest",
    "ProviderSearchQueryRequest",
    "ProviderStatQueryRequest",
]

UpgradeMode = Literal["MANUAL", "AUTO"]


class Plugin(BaseModel):
    plugin_id: str = None
    version: Union[str, None] = None
    options: dict
    upgrade_mode: Union[UpgradeMode, None] = None


class ProviderCreateRequest(BaseModel):
    provider: str
    name: str
    alias: Union[str, None] = None
    plugin_info: Union[Plugin, None] = None
    color: Union[str, None] = None
    icon: Union[str, None] = None
    order: Union[int, None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class ProviderUpdateRequest(BaseModel):
    provider: str
    name: Union[str, None] = None
    alias: Union[str, None] = None
    color: Union[str, None] = None
    icon: Union[str, None] = None
    order: Union[int, None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class ProviderUpdatePluginRequest(BaseModel):
    provider: str
    version: Union[str, None] = None
    options: Union[dict, None] = None
    upgrade_mode: Union[str, None] = None
    domain_id: str


class ProviderDeleteRequest(BaseModel):
    provider: str
    domain_id: str


class ProviderGetRequest(BaseModel):
    provider: str
    domain_id: str


class ProviderSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    provider: Union[str, None] = None
    name: Union[str, None] = None
    alias: Union[str, None] = None
    is_managed: Union[bool, None] = None
    domain_id: str


class ProviderStatQueryRequest(BaseModel):
    query: dict = None
    domain_id: str
