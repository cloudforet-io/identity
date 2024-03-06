from typing import Union
from pydantic import BaseModel

__all__ = ["AccountCollectorInitRequest", "AccountCollectorSyncRequest"]


class AccountCollectorInitRequest(BaseModel):
    options: dict
    domain_id: str


class AccountCollectorSyncRequest(BaseModel):
    options: dict
    schema_id: Union[dict, None] = None
    secret_data: dict
    domain_id: str
