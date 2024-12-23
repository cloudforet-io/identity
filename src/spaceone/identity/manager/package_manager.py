import logging
from typing import Tuple

from mongoengine import QuerySet
from spaceone.core.manager import BaseManager
from spaceone.core import cache

from spaceone.identity.model.package.database import Package
from spaceone.identity.manager.managed_resource_manager import ManagedResourceManager

_LOGGER = logging.getLogger(__name__)


class PackageManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.package_model = Package

    def create_package(self, params: dict) -> Package:
        def _rollback(vo: Package):
            _LOGGER.info(
                f"[create_package._rollback] Delete package: {vo.package_id} ({vo.name})"
            )
            vo.delete()

        package_vo = self.package_model.create(params)

        self.transaction.add_rollback(_rollback, package_vo)

        return package_vo

    def update_package_by_vo(self, params: dict, package_vo: Package) -> Package:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_package_by_vo._rollback] Revert Data: {old_data["package_id"]}'
            )
            package_vo.update(old_data)

        self.transaction.add_rollback(_rollback, package_vo.to_dict())
        return package_vo.update(params)

    @staticmethod
    def delete_package_by_vo(package_vo: Package) -> None:
        package_vo.delete()

    def get_package(self, package_id: str, domain_id: str) -> Package:
        return self.package_model.get(package_id=package_id, domain_id=domain_id)

    def filter_packages(self, **conditions) -> QuerySet:
        return self.package_model.filter(**conditions)

    def list_packages(self, query: dict, domain_id: str) -> Tuple[QuerySet, int]:
        self._create_managed_package(domain_id)
        return self.package_model.query(**query)

    def stat_package(self, query: dict) -> dict:
        return self.package_model.stat(**query)

    @cache.cacheable(key="identity:managed-package:{domain_id}:sync", expire=300)
    def _create_managed_package(self, domain_id: str) -> bool:
        managed_resource_mgr = ManagedResourceManager()

        package_vos = self.filter_packages(domain_id=domain_id)

        if package_vos.count() == 0:
            managed_package_map = managed_resource_mgr.get_managed_packages()

            for managed_package, managed_package_info in managed_package_map.items():
                managed_package_info["domain_id"] = domain_id
                self.create_package(managed_package_info)

        return True
