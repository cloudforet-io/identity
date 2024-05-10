from datetime import datetime, timedelta
from typing import Union, Tuple

from spaceone.core.error import ERROR_EXIST_RESOURCE
from spaceone.core.service import (
    authentication_handler,
    authorization_handler,
    mutation_handler,
)
from spaceone.core.service import (
    BaseService,
    event_handler,
    transaction,
    convert_model,
    append_query_filter,
    append_keyword_filter,
)

from spaceone.identity.manager.agent_manager import AgentManager
from spaceone.identity.manager.app_manager import AppManager
from spaceone.identity.manager.client_secret_manager import ClientSecretManager
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.model import App, Agent
from spaceone.identity.model.agent.request import (
    AgentCreateRequest,
    AgentEnableRequest,
    AgentDisableRequest,
    AgentRegenerateRequest,
    AgentDeleteRequest,
    AgentGetRequest,
    AgentSearchQueryRequest,
)
from spaceone.identity.model.agent.response import AgentResponse, AgentsResponse


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class AgentService(BaseService):
    resource = "Agent"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_mgr = AgentManager()
        self.service_account_mgr = ServiceAccountManager()
        self.app_mgr = AppManager()

    @transaction(
        permission="identity:Agent.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def create(self, params: AgentCreateRequest) -> Union[AgentResponse, dict]:
        """create agent using service account

         Args:
            params (AgentCreateRequest): {
                'service_account_id': 'str',            # required
                'options': 'dict',
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AgentResponse:
        """
        service_account_id = params.service_account_id
        options = params.options or {}
        workspace_id = params.workspace_id
        domain_id = params.domain_id
        user_projects = params.user_projects

        service_account_vo = self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        agent_vos = self.agent_mgr.filter_agents(
            domain_id=domain_id,
            workspace_id=workspace_id,
            project_id=service_account_vo.project_id,
            service_account_id=service_account_id,
        )
        if agent_vos:
            raise ERROR_EXIST_RESOURCE(
                child="Agent", parent=f"service_account({service_account_id})"
            )

        create_app_params = {
            "name": f"{service_account_vo.name} App",
            "is_managed": True,
            "role_type": "WORKSPACE_OWNER",
            "role_id": "managed-workspace-owner",
            "resource_group": "WORKSPACE",
            "domain_id": domain_id,
            "workspace_id": workspace_id,
            "service_account_id": service_account_id,
            "options": options,
            "expired_at": self._get_expired_at(),
        }

        app_vo = self.app_mgr.create_app(create_app_params)

        client_id, client_secret = self._create_agent_client_secret(
            app_vo, service_account_id
        )

        app_vo = self.app_mgr.update_app_by_vo({"client_id": client_id}, app_vo)

        create_agent_params = {
            "app_id": app_vo.app_id,
            "service_account_id": service_account_id,
            "project_id": service_account_vo.project_id,
            "domain_id": domain_id,
            "workspace_id": workspace_id,
            "options": options,
            "expired_at": self._get_expired_at(),
        }

        agent_vo = self.agent_mgr.create_agent(create_agent_params)

        agent_info = self._update_agent_info_with_app_vo(agent_vo, app_vo)

        return AgentResponse(**agent_info, client_secret=client_secret)

    @transaction(
        permission="identity:Agent.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def enable(self, params: AgentEnableRequest) -> Union[AgentResponse, dict]:
        """enable agent created by service account

         Args:
            params (AgentEnableRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AgentResponse:
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        agent_vo = self.agent_mgr.get_agent(
            service_account_id, domain_id, workspace_id, user_projects
        )
        app_vo = self.app_mgr.get_app(agent_vo.app_id, domain_id, workspace_id)
        app_vo = self.app_mgr.enable_app(app_vo)

        agent_info = self._update_agent_info_with_app_vo(agent_vo, app_vo)

        return AgentResponse(**agent_info)

    @transaction(
        permission="identity:Agent.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def disable(self, params: AgentDisableRequest) -> Union[AgentResponse, dict]:
        """disable agent created by service account

         Args:
            params (AgentDisableRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AgentResponse:
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        agent_vo = self.agent_mgr.get_agent(
            service_account_id, domain_id, workspace_id, user_projects
        )
        app_vo = self.app_mgr.get_app(agent_vo.app_id, domain_id, workspace_id)
        app_vo = self.app_mgr.disable_app(app_vo)

        agent_info = self._update_agent_info_with_app_vo(agent_vo, app_vo)

        return AgentResponse(**agent_info)

    @transaction(
        permission="identity:Agent.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def regenerate(self, params: AgentRegenerateRequest) -> Union[AgentResponse, dict]:
        """regenerate agent created by service account

         Args:
            params (ServiceAccountRegenerateAppRequest): {
                'service_account_id': 'str',            # required
                'workspace_id': 'str',                  # injected from auth (required)
                'domain_id': 'str',                     # injected from auth (required)
                'user_projects': 'list'                 # injected from auth
            }

        Returns:
            AgentResponse:
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        agent_vo = self.agent_mgr.get_agent(
            service_account_id, domain_id, workspace_id, user_projects
        )

        app_vo = self.app_mgr.get_app(agent_vo.app_id, domain_id, workspace_id)

        client_id, client_secret = self._create_agent_client_secret(
            app_vo, service_account_id
        )

        app_vo = self.app_mgr.update_app_by_vo({"client_id": client_id}, app_vo)

        agent_info = self._update_agent_info_with_app_vo(agent_vo, app_vo)

        return AgentResponse(**agent_info, client_secret=client_secret)

    @transaction(
        permission="identity:Agent.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def delete(self, params: AgentDeleteRequest) -> None:
        """delete agent created by service account

        Args:
            params (AgentDeleteRequest): {
                'service_account_id: 'str'   # required
                'workspace_id': 'str',       # injected from auth (required)
                'domain_id': 'str'           # injected from auth (required)
                'user_projects': 'list'      # injected from auth
            }
        Returns:
            None
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        self.service_account_mgr.get_service_account(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        agent_vo: Agent = self.agent_mgr.get_agent(
            service_account_id, domain_id, workspace_id, user_projects
        )

        app_vo = self.app_mgr.get_app(
            agent_vo.app_id,
            domain_id,
            workspace_id,
        )
        self.app_mgr.delete_app_by_vo(app_vo)
        self.agent_mgr.delete_agent_by_vo(agent_vo)

    @transaction(
        permission="identity:Agent.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: AgentGetRequest) -> Union[AgentResponse, dict]:
        """Get agent info
        Args:
            params (dict): {
                'service_account_id': 'str',          # required
                'workspace_id': 'list',               # injected from auth
                'domain_id': 'str'                    # injected from auth (required)
                'user_projects': 'list'               # injected from auth
            }
        Returns:
            AgentResponse:
        """
        service_account_id = params.service_account_id
        domain_id = params.domain_id
        workspace_id = params.workspace_id
        user_projects = params.user_projects

        agent_vo = self.agent_mgr.get_agent(
            service_account_id,
            domain_id,
            workspace_id,
            user_projects,
        )

        app_vo = self.app_mgr.get_app(agent_vo.app_id, domain_id, workspace_id)

        agent_info = self._update_agent_info_with_app_vo(agent_vo, app_vo)

        return AgentResponse(**agent_info)

    @transaction(
        permission="identity:Agent.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        [
            "agent_id",
            "service_account_id",
            "state",
            "workspace_id",
            "domain_id",
            "user_projects",
        ]
    )
    @append_keyword_filter(["agent_id", "name"])
    @convert_model
    def list(self, params: AgentSearchQueryRequest) -> Union[AgentsResponse, dict]:
        """List Agents
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'agent_id': 'str',
                'state': 'str',
                'service_account_id': 'str',  # required
                'workspace_id': 'list'        # injected from auth
                'domain_id': 'str'            # injected from auth (required)
                'user_projects': 'list'       # injected from auth
            }
        Returns:
            AgentsResponse:
        """
        query = params.query or {}
        agent_vos, agent_total_count = self.agent_mgr.list_agents(query)
        agents_info = [agent_vo.to_dict() for agent_vo in agent_vos]

        app_ids = [agent_vo.app_id for agent_vo in agent_vos]

        app_vos, app_total_count = self.app_mgr.list_apps(
            {"filter": [{"k": "app_id", "v": app_ids, "o": "in"}]}
        )

        apps_info = [app_vo.to_dict() for app_vo in app_vos]

        agents_info = self._update_agents_info_with_apps_info(agents_info, apps_info)

        return AgentsResponse(results=agents_info, total_count=len(agents_info))

    def _create_agent_client_secret(
        self, app_vo: App, service_account_id: str
    ) -> Tuple[str, str]:
        """create client_id, client_secret for agent created by service account

        Args:
            app_vo: 'App'                   # required
            service_account_id: 'str'       # required

        Returns:
            tuple: ('client_id': 'str', 'client_secret': 'str')
        """
        permissions = ["identity:ServiceAccount.read"]
        injected_params = {"service_account_id": service_account_id}
        expired_at = self._get_expired_at()

        client_secret_mgr = ClientSecretManager()
        client_id, client_secret = client_secret_mgr.generate_client_secret(
            app_vo.app_id,
            app_vo.domain_id,
            expired_at,
            app_vo.role_type,
            app_vo.workspace_id,
            permissions=permissions,
            injected_params=injected_params,
        )

        return client_id, client_secret

    @staticmethod
    def _update_agent_info_with_app_vo(agent_vo, app_vo):
        agent_info = agent_vo.to_dict()
        agent_info["state"] = app_vo.state
        agent_info["is_managed"] = app_vo.is_managed
        agent_info["role_type"] = app_vo.role_type
        agent_info["role_id"] = app_vo.role_id
        agent_info["app_id"] = app_vo.app_id
        agent_info["client_id"] = app_vo.client_id
        agent_info["expired_at"] = app_vo.expired_at
        agent_info["last_accessed_at"] = app_vo.last_accessed_at

        return agent_info

    @staticmethod
    def _update_agents_info_with_apps_info(agents_info, apps_info):
        agents_info_with_apps_info = []

        for agent_info, app_info in zip(agents_info, apps_info):
            agent_info.update(
                {
                    "state": app_info["state"],
                    "is_managed": app_info["is_managed"],
                    "role_type": app_info["role_type"],
                    "role_id": app_info["role_id"],
                    "app_id": app_info["app_id"],
                    "client_id": app_info["client_id"],
                    "expired_at": app_info["expired_at"],
                    "last_accessed_at": app_info["last_accessed_at"],
                }
            )
            agents_info_with_apps_info.append(agent_info)

        return agents_info_with_apps_info

    @staticmethod
    def _get_expired_at() -> str:
        return (datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
