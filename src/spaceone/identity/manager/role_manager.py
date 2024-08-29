import logging
from typing import Tuple

from mongoengine import QuerySet
from spaceone.core import cache, utils
from spaceone.core.manager import BaseManager

from spaceone.identity.error.error_role import ERROR_ROLE_IN_USED
from spaceone.identity.manager.managed_resource_manager import ManagedResourceManager
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.model.role.database import Role

_LOGGER = logging.getLogger(__name__)


class RoleManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_model = Role

    def create_role(self, params: dict) -> Role:
        def _rollback(vo: Role):
            _LOGGER.info(
                f"[create_role._rollback] Delete role: {vo.name} ({vo.role_id})"
            )
            vo.delete()

        if "role_id" not in params:
            params["role_id"] = utils.generate_id("role")

        if api_permissions := params.get("api_permissions"):
            params["api_permissions"] = list(set(api_permissions))

        role_vo = self.role_model.create(params)
        self.transaction.add_rollback(_rollback, role_vo)

        return role_vo

    def update_role_by_vo(self, params: dict, role_vo: Role) -> Role:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_role_by_vo._rollback] Revert Data: {old_data["role_id"]}'
            )
            role_vo.update(old_data)

        if api_permissions := params.get("api_permissions"):
            params["api_permissions"] = list(set(api_permissions))

        self.transaction.add_rollback(_rollback, role_vo.to_dict())

        return role_vo.update(params)

    def enable_role_by_vo(self, role_vo: Role) -> Role:
        self.update_role_by_vo({"state": "ENABLED"}, role_vo)
        return role_vo

    def disable_role_by_vo(self, role_vo: Role) -> Role:
        self.update_role_by_vo({"state": "DISABLED"}, role_vo)
        return role_vo

    @staticmethod
    def delete_role_by_vo(role_vo: Role) -> None:
        rb_mgr = RoleBindingManager()
        rb_vos = rb_mgr.filter_role_bindings(
            role_id=role_vo.role_id, domain_id=role_vo.domain_id
        )

        for rb_vo in rb_vos:
            raise ERROR_ROLE_IN_USED(
                role_binding_id=rb_vo.role_binding_id, user_id=rb_vo.user_id
            )

        role_vo.delete()

    def get_role(self, role_id: str, domain_id: str) -> Role:
        return self.role_model.get(role_id=role_id, domain_id=domain_id)

    def filter_roles(self, **conditions) -> QuerySet:
        return self.role_model.filter(**conditions)

    def list_roles(self, query: dict, domain_id: str) -> Tuple[QuerySet, int]:
        self._create_managed_role(domain_id)
        return self.role_model.query(**query)

    def stat_roles(self, query: dict) -> dict:
        return self.role_model.stat(**query)

    @cache.cacheable(key="identity:managed-role:{domain_id}:sync", expire=300)
    def _create_managed_role(self, domain_id: str) -> bool:
        managed_resource_mgr = ManagedResourceManager()

        role_vos = self.filter_roles(domain_id=domain_id, is_managed=True)

        installed_role_version_map = {}
        for role_vo in role_vos:
            installed_role_version_map[role_vo.role_id] = role_vo.version

        managed_role_map = managed_resource_mgr.get_managed_roles()

        for managed_role_id, managed_role_info in managed_role_map.items():
            managed_role_info["domain_id"] = domain_id
            managed_role_info["is_managed"] = True

            if role_version := installed_role_version_map.get(managed_role_id):
                if role_version != managed_role_info["version"]:
                    _LOGGER.debug(
                        f"[_create_managed_role] update managed role: {managed_role_id}"
                    )
                    role_vo = self.get_role(managed_role_id, domain_id)
                    self.update_role_by_vo(managed_role_info, role_vo)
            else:
                _LOGGER.debug(
                    f"[_create_managed_role] create new managed role: {managed_role_id}"
                )
                self.create_role(managed_role_info)

        return True
