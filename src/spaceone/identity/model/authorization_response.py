from typing import Union, Literal, List
from pydantic import BaseModel

from spaceone.identity.model.authorization_request import RoleType


class AuthorizationResponse(BaseModel):
    role_type: Union[RoleType, None] = None
    projects: Union[List[str], None] = None
    workspaces: Union[List[str], None] = None
