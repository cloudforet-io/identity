import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)


class OpsflowManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opsflow_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="opsflow"
        )

    def list_task_categories_by_package(self, domain_id: str, package_id: str) -> dict:
        params = {
            "query": {
                "filter": [
                    {"k": "package_id", "v": package_id, "o": "eq"},
                ]
            }
        }

        return self.opsflow_conn.dispatch(
            "TaskCategory.list",
            params,
            x_domain_id=domain_id,
        )
