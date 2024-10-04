import logging
from typing import Dict, List, Tuple

from mongoengine import QuerySet
from spaceone.core.error import ERROR_INVALID_PARAMETER, ERROR_NOT_FOUND
from spaceone.core.manager import BaseManager

from spaceone.identity.error import (
    ERROR_USER_EXIST_IN_WORKSPACE_GROUP,
    ERROR_WORKSPACE_EXIST_IN_WORKSPACE_GROUP,
)
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.manager.workspace_manager import WorkspaceManager
from spaceone.identity.model.workspace_group.database import WorkspaceGroup

_LOGGER = logging.getLogger(__name__)


class WorkspaceGroupManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_group_model = WorkspaceGroup
        self.workspace_manager = WorkspaceManager()
        self.rb_mgr = RoleBindingManager()

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

    def delete_workspace_group_by_vo(self, workspace_group_vo: WorkspaceGroup) -> None:
        workspace_vos = self.workspace_manager.filter_workspaces(
            workspace_group_id=workspace_group_vo.workspace_group_id,
            domain_id=workspace_group_vo.domain_id,
        )
        self._check_existence_of_workspace_or_user(workspace_vos, workspace_group_vo)

        workspace_group_vo.delete()

    def get_workspace_group(
        self, domain_id: str, workspace_group_id: str, user_id: str = None
    ) -> WorkspaceGroup:
        conditions = {
            "domain_id": domain_id,
            "workspace_group_id": workspace_group_id,
        }

        if user_id:
            conditions["users__user_id"] = user_id

        return self.workspace_group_model.get(**conditions)

    def filter_workspace_groups(self, **conditions) -> QuerySet:
        return self.workspace_group_model.filter(**conditions)

    def list_workspace_groups(self, query: dict) -> Tuple[QuerySet, int]:
        return self.workspace_group_model.query(**query)

    def stat_workspace_group(self, query: dict) -> dict:
        return self.workspace_group_model.stat(**query)

    def get_workspace_group_with_users(
        self, domain_id: str, workspace_group_id: str
    ) -> Tuple[WorkspaceGroup, List[str]]:
        workspace_group_vo = self.get_workspace_group(domain_id, workspace_group_id)

        workspace_group_user_ids = []
        if workspace_group_vo.users:
            old_users, new_users = self.get_unique_user_ids(
                domain_id, workspace_group_id, workspace_group_vo.users
            )
            workspace_group_user_ids = old_users + new_users

        return workspace_group_vo, workspace_group_user_ids

    @staticmethod
    def _check_existence_of_workspace_or_user(
        workspace_vos: QuerySet, workspace_group_vo: WorkspaceGroup
    ) -> None:
        for workspace_vo in workspace_vos:
            if workspace_vo:
                _LOGGER.error(
                    f"Workspace exists in Workspace Group. ({workspace_vo.workspace_id}, {workspace_group_vo.workspace_group_id})"
                    "Remove the workspace from the workspace group before deleting the workspace group."
                )
                raise ERROR_WORKSPACE_EXIST_IN_WORKSPACE_GROUP(
                    workspace_id=workspace_vo.workspace_id,
                    workspace_group_id=workspace_group_vo.workspace_group_id,
                )

        if users := workspace_group_vo.users:
            for user in users:
                _LOGGER.error(
                    f"User exists in Workspace Group. ({user['user_id']}, {workspace_group_vo.workspace_group_id})"
                    "Remove the user from the workspace group before deleting the workspace group."
                )
                raise ERROR_USER_EXIST_IN_WORKSPACE_GROUP(
                    user_id=user["user_id"],
                    workspace_group_id=workspace_group_vo.workspace_group_id,
                )

    @staticmethod
    def check_user_id_in_users(user_id: str, workspace_group_vo: WorkspaceGroup):
        return any(
            workspace_group_user_id == user_id
            for workspace_group_user_id in workspace_group_vo["users"]
        )

    def get_unique_user_ids(
        self,
        domain_id: str,
        workspace_group_id: str,
        new_users_info_list: List[Dict[str, str]],
    ) -> Tuple[List[str], List[str]]:
        workspace_group_vo = self.get_workspace_group(domain_id, workspace_group_id)

        old_user_ids = []
        if users := workspace_group_vo.users:
            unique_user_ids = {user["user_id"] for user in users}
            old_user_ids = list(unique_user_ids)

        new_user_ids = []
        for new_user_info in new_users_info_list:
            unique_user_ids = {new_user_info["user_id"]}
            new_user_ids = list(unique_user_ids)

        return old_user_ids, new_user_ids

    @staticmethod
    def check_new_users_already_in_workspace_group(
        old_user_ids: List[str], new_user_ids: List[str]
    ) -> None:
        if set(old_user_ids) & set(new_user_ids):
            _LOGGER.error(
                f"Users {new_user_ids} is already in workspace group or not registered."
            )
            raise ERROR_INVALID_PARAMETER(
                key="users",
                reason=f"User {new_user_ids} is already in the workspace group or not registered.",
            )

    @staticmethod
    def check_user_ids_exist_in_workspace_group(
        old_user_ids: List[str], user_ids: List[str]
    ) -> None:
        for user_id in user_ids:
            if user_id not in old_user_ids:
                _LOGGER.error(f"User ID {user_id} is not in workspace group.")
                raise ERROR_NOT_FOUND(key="user_id", value=user_id)
