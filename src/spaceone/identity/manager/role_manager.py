import logging
from typing import Tuple, List

from spaceone.core import cache, utils
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.identity.model.role.database import Role
from spaceone.identity.manager.role_binding_manager import RoleBindingManager
from spaceone.identity.error.error_role import ERROR_ROLE_IN_USED

_LOGGER = logging.getLogger(__name__)


class RoleManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_model = Role

    def create_role(self, params: dict) -> Role:
        def _rollback(vo: Role):
            _LOGGER.info(f'[create_role._rollback] '
                         f'Delete role: {vo.name} ({vo.role_id})')
            vo.delete()

        params['policies'] = list(set(params['policies']))
        params['policies_hash'] = utils.dict_to_hash(
            {'policies': params['policies']}
        )
        params['page_permissions_hash'] = utils.dict_to_hash(
            {'page_permissions': params.get('page_permissions', [])}
        )

        role_vo = self.role_model.create(params)
        self.transaction.add_rollback(_rollback, role_vo)

        return role_vo

    def update_role_by_vo(
            self, params: dict, role_vo: Role
    ) -> Role:
        def _rollback(old_data):
            _LOGGER.info(f'[update_role_by_vo._rollback] Revert Data : {old_data["role_id"]}')
            role_vo.update(old_data)

        self.transaction.add_rollback(_rollback, role_vo.to_dict())

        if 'policies' in params:
            params['policies'] = list(set(params['policies']))
            params['policies_hash'] = utils.dict_to_hash(
                {'policies': params['policies']}
            )

        if 'page_permissions' in params:
            params['page_permissions_hash'] = utils.dict_to_hash(
                {'page_permissions': params['page_permissions']}
            )

        return role_vo.update(params)

    @staticmethod
    def delete_role_by_vo(role_vo: Role) -> None:
        rb_mgr = RoleBindingManager()
        rb_vos = rb_mgr.filter_role_bindings(role_id=role_vo.role_id, domain_id=role_vo.domain_id)

        for rb_vo in rb_vos:
            raise ERROR_ROLE_IN_USED(role_binding_id=rb_vo.role_binding_id, user_id=rb_vo.user_id)

        role_vo.delete()

    def get_role(self, role_id: str, domain_id: str) -> Role:
        return self.role_model.get(role_id=role_id, domain_id=domain_id)

    def filter_roles(self, **conditions) -> List[Role]:
        return self.role_model.filter(**conditions)

    def list_roles(self, query: dict) -> Tuple[list, int]:
        return self.role_model.query(**query)

    def stat_roles(self, query: dict) -> dict:
        return self.role_model.stat(**query)