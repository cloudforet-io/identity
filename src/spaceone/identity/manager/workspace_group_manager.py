import logging
from typing import Tuple

from mongoengine import QuerySet
from spaceone.core.manager import BaseManager

from spaceone.identity.model.workspace_group.database import WorkspaceGroup

_LOGGER = logging.getLogger(__name__)


class WorkspaceGroupManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_group_model = WorkspaceGroup

    def create_workspace_group(self, params: dict) -> WorkspaceGroup:
        def _rollback(vo: WorkspaceGroup):
            _LOGGER.info(
                f"[create_workspace_group._rollback] Delete workspace group : {vo.workspace_group_id} ({vo.name})"
            )
            vo.delete()

        workspace_group_vo = self.workspace_group_model.create(params)
        self.transaction.add_rollback(_rollback, workspace_group_vo)

        return workspace_group_vo

    def update_workspace_group_by_vo(
        self, params: dict, workspace_group_vo: WorkspaceGroup
    ) -> WorkspaceGroup:
        def _rollback(old_data):
            _LOGGER.info(
                f"[update_workspace_group._rollback] Revert Data : {old_data['workspace_group_id']} ({old_data['name']})"
            )
            workspace_group_vo.update(old_data)

        self.transaction.add_rollback(_rollback, workspace_group_vo.to_dict())

        return workspace_group_vo.update(params)

    @staticmethod
    def delete_workspace_group_by_vo(workspace_group_vo: WorkspaceGroup) -> None:
        workspace_group_vo.delete()

    # TODO: When add_users and remove_users, are user_id and role_type required?
    def get_workspace_group(
        self,
        workspace_group_id: str,
        domain_id: str,
        user_id: str = None,
        role_type: str = None,
    ) -> WorkspaceGroup:
        conditions = {
            "workspace_group_id": workspace_group_id,
            "domain_id": domain_id,
        }

        if user_id:
            conditions["users__user_id"] = user_id

        # TODO: Check if this is correct
        # if role_type:
        #     conditions["users__role_type"] = role_type

        return self.workspace_group_model.get(**conditions)

    def filter_workspace_groups(self, **conditions) -> QuerySet:
        return self.workspace_group_model.filter(**conditions)

    def list_workspace_groups(self, query: dict) -> Tuple[QuerySet, int]:
        return self.workspace_group_model.query(**query)

    def stat_workspace_group(self, query: dict) -> dict:
        return self.workspace_group_model.stat(**query)

    @staticmethod
    def check_user_id_in_users(user_id: str, workspace_group_vo: WorkspaceGroup):
        return any(
            workspace_group_user_id == user_id
            for workspace_group_user_id in workspace_group_vo["users"]
        )
