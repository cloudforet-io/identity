import logging

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.model.domain_db_model import Domain

_LOGGER = logging.getLogger(__name__)


class DomainManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_model = Domain()

    def create_domain(self, params):
        def _rollback(vo):
            _LOGGER.info(
                f"[create_domain._rollback] Delete domain : {vo.name} ({vo.domain_id})"
            )
            vo.delete()

        domain_vo = self.domain_model.create(params)
        self.transaction.add_rollback(_rollback, domain_vo)

        return domain_vo

    def update_domain(self, params):
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})'
            )
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(params["domain_id"])
        self.transaction.add_rollback(_rollback, domain_vo.to_dict())

        return domain_vo.update(params)

    def delete_domain(self, domain_id):
        domain_vo: Domain = self.get_domain(domain_id)
        domain_vo.delete()

        cache.delete_pattern(f"domain-state:{domain_id}")

    def enable_domain(self, domain_id):
        def _rollback(old_data):
            _LOGGER.info(
                f'[enable_domain._rollback] Revert Data : {old_data["name"]} ({old_data["domain_id"]})'
            )
            domain_vo.update(old_data)

        domain_vo: Domain = self.get_domain(domain_id)

        if domain_vo.state != "ENABLED":
            self.transaction.add_rollback(_rollback, domain_vo.to_dict())
            domain_vo.update({"state": "ENABLED"})

            cache.delete_pattern(f"domain-state:{domain_id}")

        return domain_vo

    def disable_domain(self, domain_id):
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

    def get_domain(self, domain_id):
        return self.domain_model.get(domain_id=domain_id)

    def list_domains(self, query):
        return self.domain_model.query(**query)
