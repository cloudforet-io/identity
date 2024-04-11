import logging
from typing import Tuple, Union

from mongoengine import QuerySet
from spaceone.core.manager import BaseManager

from spaceone.identity.model import Agent


_LOGGER = logging.getLogger(__name__)


class AgentManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_model = Agent

    def create_agent(self, params: dict) -> Agent:
        def _rollback(vo: Agent):
            _LOGGER.info(f"[create_agent._rollback] " f"Delete agent: ({vo.agent_id})")
            agent_vo.delete()

        agent_vo = self.agent_model.create(params)
        self.transaction.add_rollback(_rollback, agent_vo)

        return agent_vo

    def get_agent(
        self,
        service_account_id: str,
        domain_id: str,
        workspace_id: str,
        user_projects: Union[list, None] = None,
    ) -> Agent:
        conditions = {
            "service_account_id": service_account_id,
            "domain_id": domain_id,
            "workspace_id": workspace_id,
        }

        if user_projects:
            conditions["project_id"] = user_projects

        return self.agent_model.get(**conditions)

    def update_agent_by_vo(self, params: dict, agent_vo: Agent) -> Agent:
        def _rollback(old_data):
            _LOGGER.info(
                f"[update_agent_by_vo._rollback] Revert Data : "
                f"{old_data['agent_id']}"
            )
            agent_vo.update(old_data)

        self.transaction.add_rollback(_rollback, agent_vo.to_dict())

        return agent_vo.update(params)

    @staticmethod
    def delete_agent_by_vo(agent_vo: Agent) -> None:
        agent_vo.delete()

    def filter_agents(self, **conditions) -> QuerySet:
        return self.agent_model.filter(**conditions)

    def list_agents(self, query: dict) -> Tuple[list, int]:
        return self.agent_model.query(**query)
