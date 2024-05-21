from typing import Union
from pydantic import BaseModel


__all__ = ["ExternalAuthInitRequest", "ExternalAuthAuthorizeRequest"]


class ExternalAuthInitRequest(BaseModel):
    options: dict
    domain_id: str


class ExternalAuthAuthorizeRequest(BaseModel):
    options: dict
    schema_id: Union[dict, None] = None
    secret_data: dict
    credentials: dict
    domain_id: str
