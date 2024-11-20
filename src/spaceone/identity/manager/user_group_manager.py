import logging
from typing import Tuple

from mongoengine import QuerySet
from spaceone.core.manager import BaseManager

from spaceone.identity.model.user_group.database import UserGroup

_LOGGER = logging.getLogger(__name__)


class UserGroupManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_group_model = UserGroup

    def create_user_group(self, params: dict) -> UserGroup:
        def _rollback(vo: UserGroup):
            _LOGGER.info(
                f"[create_user_group._rollback] Delete user_group: {vo.user_group_id} ({vo.name})"
            )
            vo.delete()

        user_group_vo = self.user_group_model.create(params)

        self.transaction.add_rollback(_rollback, user_group_vo)

        return user_group_vo

    def update_user_group_by_vo(
        self, params: dict, user_group_vo: UserGroup
    ) -> UserGroup:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_user_group_by_vo._rollback] Revert Data: {old_data["user_group_id"]}'
            )
            user_group_vo.update(old_data)

        self.transaction.add_rollback(_rollback, user_group_vo.to_dict())
        return user_group_vo.update(params)

    @staticmethod
    def delete_user_group_by_vo(user_group_vo: UserGroup) -> None:
        user_group_vo.delete()

    def get_user_group(
        self, user_group_id: str, domain_id: str, workspace_id: str = None
    ) -> UserGroup:
        conditions = {"user_group_id": user_group_id, "domain_id": domain_id}

        if workspace_id:
            conditions["workspace_id"] = workspace_id

        return self.user_group_model.get(**conditions)

    def filter_user_groups(self, **conditions) -> QuerySet:
        return self.user_group_model.filter(**conditions)

    def list_user_groups(self, query: dict) -> Tuple[QuerySet, int]:
        return self.user_group_model.query(**query)

    def stat_user_group(self, query: dict) -> dict:
        return self.user_group_model.stat(**query)
