from datetime import datetime
from typing import Union, List
from pydantic import BaseModel
from spaceone.core import utils

from spaceone.identity.model.provider.request import UpgradeMode

__all__ = ["ProviderResponse", "ProvidersResponse"]


class Plugin(BaseModel):
    plugin_id: str = None
    version: Union[str, None] = None
    options: Union[dict, None] = None
    upgrade_mode: Union[UpgradeMode, None] = None
    metadata: Union[dict, None] = None


class ProviderResponse(BaseModel):
    provider: Union[str, None] = None
    name: Union[str, None] = None
    plugin_info: Union[Plugin, None] = None
    alias: Union[str, None] = None
    color: Union[str, None] = None
    icon: Union[str, None] = None
    order: Union[int, None] = None
    options: Union[dict, None] = None
    tags: Union[dict, None] = None
    is_managed: Union[bool, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["updated_at"] = utils.datetime_to_iso8601(data["updated_at"])
        return data


class ProvidersResponse(BaseModel):
    results: List[ProviderResponse] = []
    total_count: int
