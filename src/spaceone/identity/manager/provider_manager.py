import logging
from typing import Tuple, List

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.model.provider.database import Provider
from spaceone.identity.manager.managed_resource_manager import ManagedResourceManager

_LOGGER = logging.getLogger(__name__)


class ProviderManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_model = Provider

    def create_provider(self, params: dict) -> Provider:
        def _rollback(vo: Provider):
            _LOGGER.info(f"[create_provider._rollback] Delete provider : {vo.provider}")
            vo.delete()

        provider_vo = self.provider_model.create(params)
        self.transaction.add_rollback(_rollback, provider_vo)

        return provider_vo

    def update_provider_by_vo(self, params: dict, provider_vo: Provider) -> Provider:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_provider._rollback] Revert Data : {old_data["provider"]}'
            )
            provider_vo.update(old_data)

        self.transaction.add_rollback(_rollback, provider_vo.to_dict())

        return provider_vo.update(params)

    @staticmethod
    def delete_provider_by_vo(provider_vo: Provider) -> None:
        provider_vo.delete()

    def get_provider(self, provider: str, domain_id: str) -> Provider:
        return self.provider_model.get(provider=provider, domain_id=domain_id)

    def filter_providers(self, **conditions) -> List[Provider]:
        return self.provider_model.filter(**conditions)

    def list_providers(self, query: dict, domain_id: str) -> Tuple[list, int]:
        self._create_managed_provider(domain_id)
        return self.provider_model.query(**query)

    def stat_providers(self, query: dict) -> dict:
        return self.provider_model.stat(**query)

    @cache.cacheable(key="identity:managed-provider:{domain_id}:sync", expire=300)
    def _create_managed_provider(self, domain_id: str) -> bool:
        managed_resource_mgr = ManagedResourceManager()

        provider_vos = self.filter_providers(domain_id=domain_id, is_managed=True)

        installed_provider_version_map = {}
        for provider_vo in provider_vos:
            installed_provider_version_map[provider_vo.provider] = provider_vo.version

        managed_provider_map = managed_resource_mgr.get_managed_providers()

        for managed_provider, managed_provider_info in managed_provider_map.items():
            managed_provider_info["domain_id"] = domain_id
            managed_provider_info["is_managed"] = True

            if provider_version := installed_provider_version_map.get(managed_provider):
                if provider_version != managed_provider_info["version"]:
                    _LOGGER.debug(
                        f"[_create_managed_provider] update managed provider: {managed_provider}"
                    )
                    provider_vo = self.get_provider(managed_provider, domain_id)
                    self.update_provider_by_vo(managed_provider_info, provider_vo)
            else:
                _LOGGER.debug(
                    f"[_create_managed_provider] create new managed provider: {managed_provider}"
                )
                self.create_provider(managed_provider_info)

        return True
