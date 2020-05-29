import logging
from spaceone.core.manager import BaseManager
from spaceone.identity.model.policy_model import *
from spaceone.identity.model.role_model import *

_LOGGER = logging.getLogger(__name__)


class RoleManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_model: Role = self.locator.get_model('Role')

    def create_role(self, params):
        def _rollback(role_vo):
            _LOGGER.info(f'[create_role._rollback] Delete role : {role_vo.name} ({role_vo.role_id})')
            role_vo.delete()

        role_vo = self.role_model.create(params)
        self.transaction.add_rollback(_rollback, role_vo)

        return role_vo

    def update_role(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_role._rollback] Revert Data : {old_data["name"], ({old_data["role_id"]})}')
            role_vo.update(old_data)

        role_vo: Role = self.get_role(params['role_id'], params['domain_id'])
        self.transaction.add_rollback(_rollback, role_vo.to_dict())

        return role_vo.update(params)

    def delete_role(self, role_id, domain_id):
        role_vo = self.get_role(role_id, domain_id)
        role_vo.delete()

    def get_role(self, role_id, domain_id, only=None):
        return self.role_model.get(role_id=role_id, domain_id=domain_id, only=only)

    def list_roles(self, query):
        return self.role_model.query(**query)

    def stat_roles(self, query):
        return self.role_model.stat(**query)
