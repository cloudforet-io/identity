from datetime import datetime
from typing import Union, Literal, List
from pydantic import BaseModel
from spaceone.core import utils
from spaceone.identity.model.trusted_account.request import ResourceGroup

__all__ = ["TrustedAccountResponse", "TrustedAccountsResponse"]


class TrustedAccountResponse(BaseModel):
    trusted_account_id: Union[str, None] = None
    name: Union[str, None] = None
    data: Union[dict, None] = None
    provider: Union[str, None] = None
    schedule: Union[dict, None] = None
    sync_options: Union[dict, None] = None
    plugin_options: Union[dict, None] = None
    tags: Union[dict, None] = None
    secret_schema_id: Union[str, None] = None
    trusted_secret_id: Union[str, None] = None
    resource_group: Union[ResourceGroup, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        return data


class TrustedAccountsResponse(BaseModel):
    results: List[TrustedAccountResponse]
    total_count: int
