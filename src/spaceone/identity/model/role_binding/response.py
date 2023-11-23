from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.identity.model.role_binding.request import Scope

__all__ = ["RoleBindingResponse", "RoleBindingsResponse"]


class RoleBindingResponse(BaseModel):
    role_binding_id: Union[str, None] = None
    scope: Union[Scope, None] = None
    user_id: Union[str, None] = None
    role_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None


class RoleBindingsResponse(BaseModel):
    results: List[RoleBindingResponse]
    total_count: int
