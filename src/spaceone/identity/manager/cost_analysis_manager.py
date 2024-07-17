import logging

from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)


class CostAnalysisManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cost_analysis_conn: SpaceConnector = self.locator.get_connector(
            "SpaceConnector", service="cost_analysis"
        )

    def list_cost_reports(
        self, params: dict, token: str = None, x_domain_id: str = None
    ) -> dict:
        return self.cost_analysis_conn.dispatch(
            "CostReport.list",
            params,
            token=token,
            x_domain_id=x_domain_id,
        )
