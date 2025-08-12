import logging
from typing import Tuple

from mongoengine import QuerySet

from spaceone.core.manager import BaseManager
from spaceone.identity.manager.user_group_manager import UserGroupManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.role_binding.database import RoleBinding

_LOGGER = logging.getLogger(__name__)


class RoleBindingManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_binding_model = RoleBinding

    def create_role_binding(self, params: dict) -> RoleBinding:
        def _rollback(vo: RoleBinding):
            _LOGGER.info(f"[create_role_binding._rollback]: {vo.role_binding_id}")
            vo.delete()

        role_binding_vo = self.role_binding_model.create(params)
        self.transaction.add_rollback(_rollback, role_binding_vo)

        if role_binding_vo.workspace_id and role_binding_vo.workspace_id != "*":
            self._update_workspace_user_count(
                role_binding_vo.workspace_id, role_binding_vo.domain_id
            )

        return role_binding_vo

    def update_role_binding_by_vo(
        self, params: dict, role_binding_vo: RoleBinding
    ) -> RoleBinding:
        def _rollback(old_data):
            _LOGGER.info(
                f"[update_role_binding_by_vo._rollback] Revert Data: "
                f"{old_data['role_binding_id']}"
            )
            role_binding_vo.update(old_data)

        self.transaction.add_rollback(_rollback, role_binding_vo.to_dict())

        return role_binding_vo.update(params)

    def delete_role_binding_by_vo(
        self,
        role_binding_vo: RoleBinding,
    ) -> None:
        _LOGGER.debug(
            f"[delete_role_binding_by_vo] Delete role binding info: {role_binding_vo.to_dict()}"
        )
        role_binding_vo.delete()

        if role_binding_vo.workspace_id:
            # Delete user from user groups
            user_group_mgr = UserGroupManager()
            user_group_vos = user_group_mgr.filter_user_groups(
                users=role_binding_vo.user_id, domain_id=role_binding_vo.domain_id
            )
            for user_group_vo in user_group_vos:
                users = user_group_vo.users
                users.remove(role_binding_vo.user_id)
                user_group_mgr.update_user_group_by_vo(
                    {"users": users}, user_group_vo=user_group_vo
                )

        if role_binding_vo.workspace_id and role_binding_vo.workspace_id != "*":
            self._update_workspace_user_count(
                role_binding_vo.workspace_id, role_binding_vo.domain_id
            )

    def get_role_binding(
        self, role_binding_id: str, domain_id: str, workspace_id: str = None
    ) -> RoleBinding:
        conditions = {
            "role_binding_id": role_binding_id,
            "domain_id": domain_id,
        }

        if workspace_id:
            conditions["workspace_id"] = workspace_id

        return self.role_binding_model.get(**conditions)

    def filter_role_bindings(self, **conditions) -> QuerySet:
        return self.role_binding_model.filter(**conditions)

    def list_role_bindings(self, query: dict) -> Tuple[QuerySet, int]:
        return self.role_binding_model.query(**query)

    def stat_role_bindings(self, query: dict) -> dict:
        return self.role_binding_model.stat(**query)

    def _update_workspace_user_count(self, workspace_id: str, domain_id: str) -> None:
        workspace_mgr = WorkspaceManager()

        workspace_vo = workspace_mgr.get_workspace(workspace_id, domain_id)

        if workspace_vo and workspace_vo.workspace_id != "*":
            user_rb_total_count = self._get_workspace_user_count(
                workspace_id, domain_id
            )

            workspace_mgr.update_workspace_by_vo(
                {"user_count": user_rb_total_count}, workspace_vo
            )

    def _get_workspace_user_count(self, workspace_id: str, domain_id: str) -> int:
        user_rb_ids = self.stat_role_bindings(
            query={
                "distinct": "user_id",
                "filter": [
                    {"k": "workspace_id", "v": workspace_id, "o": "eq"},
                    {"k": "domain_id", "v": domain_id, "o": "eq"},
                ],
            }
        ).get("results", [])

        return len(user_rb_ids)
