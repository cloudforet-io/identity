import logging
from typing import Tuple, List
from mongoengine import QuerySet

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.identity.model.service_account.database import ServiceAccount

_LOGGER = logging.getLogger(__name__)


class ServiceAccountManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_account_model = ServiceAccount

    def create_service_account(self, params: dict) -> ServiceAccount:
        def _rollback(vo: ServiceAccount):
            _LOGGER.info(
                f"[create_service_account._rollback] "
                f"Delete service account: {vo.name} ({vo.service_account_id})"
            )
            service_account_vo.delete()

        params["state"] = "ACTIVE"
        params["cost_info"] = {
            "day": 0,
            "month": 0,
        }

        service_account_vo = self.service_account_model.create(params)
        self.transaction.add_rollback(_rollback, service_account_vo)

        return service_account_vo

    def update_service_account(self, params: dict) -> ServiceAccount:
        service_account_vo = self.get_service_account(
            params["service_account_id"],
            params["domain_id"],
            params["workspace_id"],
            params.get("user_projects"),
        )

        return self.update_service_account_by_vo(params, service_account_vo)

    def update_service_account_by_vo(
        self, params: dict, service_account_vo: ServiceAccount
    ) -> ServiceAccount:
        def _rollback(old_data):
            _LOGGER.info(
                f"[update_service_account_by_vo._rollback] Revert Data : "
                f'{old_data["service_account_id"]}'
            )
            service_account_vo.update(old_data)

        self.transaction.add_rollback(_rollback, service_account_vo.to_dict())

        return service_account_vo.update(params)

    @staticmethod
    def delete_service_account_by_vo(service_account_vo: ServiceAccount) -> None:
        service_account_vo.delete()

    def get_service_account(
        self,
        service_account_id: str,
        domain_id: str,
        workspace_id: str = None,
        user_projects: List[str] = None,
    ) -> ServiceAccount:
        conditions = {"service_account_id": service_account_id, "domain_id": domain_id}

        if workspace_id:
            conditions["workspace_id"] = workspace_id

        if user_projects:
            conditions["project_id"] = user_projects

        return self.service_account_model.get(**conditions)

    def filter_service_accounts(self, **conditions) -> QuerySet:
        return self.service_account_model.filter(**conditions)

    def list_service_accounts(self, query: dict) -> Tuple[list, int]:
        return self.service_account_model.query(**query)

    def analyze_service_accounts(self, query: dict) -> dict:
        return self.service_account_model.analyze(**query)

    def stat_service_accounts(self, query: dict) -> dict:
        return self.service_account_model.stat(**query)

    def update_secret_project(
        self,
        service_account_id: str,
        domain_id: str,
        workspace_id: str,
        project_id: str,
    ) -> None:
        secret_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )
        response = self._list_secrets(
            secret_connector, service_account_id, domain_id, workspace_id
        )

        for secret_info in response.get("results", []):
            secret_connector.dispatch(
                "Secret.update",
                {
                    "secret_id": secret_info["secret_id"],
                    "project_id": project_id,
                    "domain_id": domain_id,
                    "workspace_id": workspace_id,
                },
            )

    def delete_secrets(
        self, service_account_id: str, domain_id: str, workspace_id: str
    ) -> None:
        secret_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )
        response = self._list_secrets(
            secret_connector, service_account_id, domain_id, workspace_id
        )

        for secret_info in response.get("results", []):
            secret_connector.dispatch(
                "Secret.delete",
                {
                    "secret_id": secret_info["secret_id"],
                    "domain_id": domain_id,
                    "workspace_id": workspace_id,
                },
            )

    def get_all_service_account_ids_using_secret(
        self, domain_id: str, workspace_id: str = None
    ) -> List[str]:
        params = {
            "query": {
                "distinct": "service_account_id",
                "filter": [{"k": "service_account_id", "v": None, "o": "not"}],
            },
            "domain_id": domain_id,
        }
        if workspace_id:
            params["workspace_id"]: workspace_id

        secret_connector: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="secret"
        )
        response = secret_connector.dispatch(
            "Secret.stat",
            params,
        )

        return response.get("results", [])

    @staticmethod
    def _list_secrets(
        secret_connector: SpaceConnector,
        service_account_id: str,
        domain_id: str,
        workspace_id: str,
    ) -> dict:
        return secret_connector.dispatch(
            "Secret.list",
            {
                "service_account_id": service_account_id,
                "domain_id": domain_id,
                "workspace_id": workspace_id,
            },
        )

    def analyze_data(self, query: dict) -> list:
        return self.service_account_model.analyze(**query)
