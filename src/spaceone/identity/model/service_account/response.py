from datetime import datetime
from typing import Union, List
from pydantic import BaseModel
from spaceone.core import utils
from spaceone.identity.model.service_account.request import State

__all__ = ["ServiceAccountResponse", "ServiceAccountsResponse"]


class ServiceAccountResponse(BaseModel):
    service_account_id: Union[str, None] = None
    name: Union[str, None] = None
    state: Union[State, None] = None
    data: Union[dict, None] = None
    provider: Union[str, None] = None
    tags: Union[dict, None] = None
    reference_id: Union[str, None] = None
    is_managed: Union[bool, None] = None
    service_account_mgr_id: Union[str, None] = None
    secret_schema_id: Union[str, None] = None
    secret_id: Union[str, None] = None
    trusted_account_id: Union[str, None] = None
    project_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    last_synced_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    inactivated_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["last_synced_at"] = utils.datetime_to_iso8601(data.get("last_synced_at"))
        data["deleted_at"] = utils.datetime_to_iso8601(data.get("deleted_at"))
        data["inactivated_at"] = utils.datetime_to_iso8601(data.get("inactivated_at"))
        return data


class ServiceAccountsResponse(BaseModel):
    results: List[ServiceAccountResponse]
    total_count: int
