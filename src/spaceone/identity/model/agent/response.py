from datetime import datetime
from typing import Union, List
from pydantic import BaseModel

from spaceone.core import utils

from spaceone.identity.model.agent.request import State, RoleType

__all__ = ["AgentResponse", "AgentsResponse"]


class AgentResponse(BaseModel):
    agent_id: Union[str, None] = None
    options: Union[dict, None] = None
    client_secret: Union[str, None] = None
    state: Union[State, None] = None
    is_managed: Union[bool, None] = None
    role_type: Union[RoleType, None] = None
    client_id: Union[str, None] = None
    role_id: Union[str, None] = None
    app_id: Union[str, None] = None
    service_account_id: Union[str, None] = None
    project_id: Union[str, None] = None
    workspace_id: Union[str, None] = None
    domain_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    expired_at: Union[datetime, None] = None
    last_accessed_at: Union[datetime, None] = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["created_at"] = utils.datetime_to_iso8601(data["created_at"])
        data["expired_at"] = utils.datetime_to_iso8601(data["expired_at"])
        data["last_accessed_at"] = utils.datetime_to_iso8601(
            data.get("last_accessed_at")
        )
        return data


class AgentsResponse(BaseModel):
    results: List[AgentResponse]
    total_count: int
