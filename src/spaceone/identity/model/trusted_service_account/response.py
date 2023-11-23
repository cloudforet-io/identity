from datetime import datetime
from typing import Union, Literal, List
from pydantic import BaseModel
from spaceone.core import utils

__all__ = ["TrustedServiceAccountResponse", "TrustedServiceAccountsResponse"]

Scope = Literal["DOMAIN", "WORKSPACE"]


class TrustedServiceAccountResponse(BaseModel):
    trusted_service_account_id: Union[str, None] = None
    name: Union[str, None] = None
    data: Union[dict, None] = None
    provider: Union[str, None] = None
    tags: Union[dict, None] = None
    scope: Union[Scope, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['created_at'] = utils.datetime_to_iso8601(data['created_at'])
        return data


class TrustedServiceAccountsResponse(BaseModel):
    results: List[TrustedServiceAccountResponse]
    total_count: int
