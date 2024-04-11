from typing import Union, Literal
from pydantic import BaseModel


__all__ = [
    "AgentCreateRequest",
    "AgentEnableRequest",
    "AgentDisableRequest",
    "AgentRegenerateRequest",
    "AgentDeleteRequest",
    "AgentGetRequest",
    "AgentSearchQueryRequest",
]

State = Literal["ENABLED", "DISABLED", "EXPIRED"]
RoleType = Literal["DOMAIN_ADMIN", "WORKSPACE_OWNER"]


class AgentCreateRequest(BaseModel):
    service_account_id: str
    options: Union[dict, None] = None
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class AgentEnableRequest(BaseModel):
    service_account_id: str
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class AgentDisableRequest(BaseModel):
    service_account_id: str
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class AgentRegenerateRequest(BaseModel):
    service_account_id: str
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class AgentDeleteRequest(BaseModel):
    service_account_id: str
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class AgentGetRequest(BaseModel):
    service_account_id: str
    workspace_id: str
    domain_id: str
    user_projects: Union[list, None] = None


class AgentSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    agent_id: Union[str, None] = None
    state: Union[State, None] = None
    service_account_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: str
    user_projects: Union[list, None] = None
