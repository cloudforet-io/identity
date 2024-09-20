from typing import Literal, Union, List
from pydantic import BaseModel

__all__ = ["TokenResponse", "GrantTokenResponse"]

RoleType = Literal["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "USER"]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class GrantTokenResponse(BaseModel):
    access_token: str
    role_type: RoleType
    role_id: Union[str, None] = None
    domain_id: str
    workspace_id: Union[str, None] = None
