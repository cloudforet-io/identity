from datetime import datetime
from typing import Union, Literal, List
from pydantic import BaseModel

__all__ = ["ServiceAccountResponse", "ServiceAccountsResponse"]

Scope = Literal["DOMAIN", "WORKSPACE"]


class ServiceAccountResponse(BaseModel):
    service_account_id: Union[str, None] = None
    name: Union[str, None] = None
    data: Union[dict, None] = None
    provider: Union[str, None] = None
    tags: Union[dict, None] = None
    trusted_service_account_id: Union[str, None] = None
    project_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None


class ServiceAccountsResponse(BaseModel):
    results: List[ServiceAccountResponse]
    total_count: int
