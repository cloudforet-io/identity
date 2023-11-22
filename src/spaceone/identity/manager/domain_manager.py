import logging
from datetime import datetime

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.core.utils import datetime_to_iso8601

from spaceone.identity.model.domain.database import Domain

_LOGGER = logging.getLogger(__name__)


class DomainManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_model = Domain

    def create_domain(self, params: dict) -> Domain:
        def _rollback(vo):
            _LOGGER.info(
                f"[create_domain._rollback] Delete domain : {vo.name} ({vo.domain_id})"
            )
            vo.delete()

        domain_vo = self.domain_model.create(params)
        self.transaction.add_rollback(_rollback, domain_vo)

        return domain_vo

    def update_domain_by_vo(self, params: dict, domain_vo: Domain) -> Domain:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})'
            )
            domain_vo.update(old_data)

            self.transaction.add_rollback(_rollback, domain_vo.to_dict())

        return domain_vo.update(params)

    @staticmethod
    def delete_domain_by_vo(domain_vo: Domain) -> None:
        domain_vo.delete()

        cache.delete_pattern(f"domain-state:{domain_vo.domain_id}")

    def enable_domain(self, domain_vo: Domain) -> Domain:
        def _rollback(old_data):
            _LOGGER.info(
                f'[enable_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})'
            )
            domain_vo.update(old_data)

        if domain_vo.state != "ENABLED":
            self.transaction.add_rollback(_rollback, domain_vo.to_dict())
            domain_vo.update({"state": "ENABLED"})

            cache.delete_pattern(f"domain-state:{domain_vo.domain_id}")

        return domain_vo

    def disable_domain(self, domain_id: str) -> Domain:
        def _rollback(old_data):
            _LOGGER.info(
                f'[disable_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})'
            )
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(domain_id)

        if domain_vo.state != "DISABLED":
            self.transaction.add_rollback(_rollback, domain_vo.to_dict())
            domain_vo.update({"state": "DISABLED"})

            cache.delete_pattern(f"domain-state:{domain_id}")

        return domain_vo

    def get_domain(self, domain_id: str) -> Domain:
        return self.domain_model.get(domain_id=domain_id)

    def get_domain_by_name(self, name: str) -> Domain:
        return self.domain_model.get(name=name)

    def list_domains(self, query: dict) -> dict:
        return self.domain_model.query(**query)

    def stat_domains(self, query: dict) -> dict:
        return self._convert_stat_request_result(self.domain_model.stat(**query))

    @staticmethod
    def _convert_stat_request_result(stats_data: dict) -> dict:
        for index, stat_data in enumerate(stats_data["results"]):
            for key, value in stat_data.items():
                if isinstance(value, datetime):
                    stats_data["results"][index][key] = datetime_to_iso8601(value)
        return stats_data
