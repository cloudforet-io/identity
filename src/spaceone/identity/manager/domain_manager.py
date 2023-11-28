import logging
from typing import Tuple
from mongoengine import QuerySet

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.model.domain.database import Domain

_LOGGER = logging.getLogger(__name__)


class DomainManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_model = Domain

    def create_domain(self, params: dict) -> Domain:
        def _rollback(vo: Domain):
            _LOGGER.info(
                f"[create_domain._rollback] Delete domain: {vo.name} ({vo.domain_id})"
            )
            vo.delete()

        domain_vo = self.domain_model.create(params)
        self.transaction.add_rollback(_rollback, domain_vo)

        return domain_vo

    def update_domain_by_vo(self, params: dict, domain_vo: Domain) -> Domain:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_domain._rollback] Revert Data: {old_data["name"]} ({old_data["domain_id"]})'
            )
            domain_vo.update(old_data)

        self.transaction.add_rollback(_rollback, domain_vo.to_dict())

        return domain_vo.update(params)

    @staticmethod
    def delete_domain_by_vo(domain_vo: Domain) -> None:
        domain_vo.delete()
        cache.delete_pattern(f"identity:domain-state:{domain_vo.domain_id}")

    def enable_domain(self, domain_vo: Domain) -> Domain:
        self.update_domain_by_vo({"state": "ENABLED"}, domain_vo)
        cache.delete_pattern(f"identity:domain-state:{domain_vo.domain_id}")

        return domain_vo

    def disable_domain(self, domain_vo: Domain) -> Domain:
        self.update_domain_by_vo({"state": "DISABLED"}, domain_vo)
        cache.delete_pattern(f"identity:domain-state:{domain_vo.domain_id}")

        return domain_vo

    def get_domain(self, domain_id: str) -> Domain:
        return self.domain_model.get(domain_id=domain_id)

    def get_domain_by_name(self, name: str) -> Domain:
        return self.domain_model.get(name=name)

    def filter_domains(self, **conditions) -> QuerySet:
        return self.domain_model.filter(**conditions)

    def list_domains(self, query: dict) -> Tuple[QuerySet, int]:
        return self.domain_model.query(**query)

    def stat_domains(self, query: dict) -> dict:
        return self.domain_model.stat(**query)
