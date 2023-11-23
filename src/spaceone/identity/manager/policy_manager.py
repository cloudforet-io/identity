import logging
from typing import Tuple, List

from spaceone.core import cache, utils
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.identity.model.policy.database import Policy
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.error.error_role import ERROR_POLICY_IN_USED

_LOGGER = logging.getLogger(__name__)


class PolicyManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_model = Policy

    def create_policy(self, params: dict) -> Policy:
        def _rollback(vo: Policy):
            _LOGGER.info(f'[create_policy._rollback] '
                         f'Delete policy: {vo.name} ({vo.policy_id})')
            vo.delete()

        params['permissions'] = list(set(params['permissions']))
        params['permissions_hash'] = utils.dict_to_hash(
            {'permissions': params['permissions']}
        )

        policy_vo = self.policy_model.create(params)
        self.transaction.add_rollback(_rollback, policy_vo)

        return policy_vo

    def update_policy_by_vo(
            self, params: dict, policy_vo: Policy
    ) -> Policy:
        def _rollback(old_data):
            _LOGGER.info(f'[update_policy_by_vo._rollback] Revert Data : {old_data["policy_id"]}')
            policy_vo.update(old_data)

        self.transaction.add_rollback(_rollback, policy_vo.to_dict())

        if 'permissions' in params:
            params['permissions'] = list(set(params['permissions']))
            params['permissions_hash'] = utils.dict_to_hash(
                {'permissions': params['permissions']}
            )

        return policy_vo.update(params)

    @staticmethod
    def delete_policy_by_vo(policy_vo: Policy) -> None:
        # Check policy is used (role)
        role_mgr = RoleManager()
        role_vos = role_mgr.filter_roles(policies=policy_vo.policy_id, domain_id=policy_vo.domain_id)

        for role_vo in role_vos:
            raise ERROR_POLICY_IN_USED(role_id=role_vo.role_id)

        policy_vo.delete()

    def get_policy(self, policy_id: str, domain_id: str) -> Policy:
        return self.policy_model.get(policy_id=policy_id, domain_id=domain_id)

    def filter_policies(self, **conditions) -> List[Policy]:
        return self.policy_model.filter(**conditions)

    def list_policies(self, query: dict) -> Tuple[list, int]:
        return self.policy_model.query(**query)

    def stat_policies(self, query: dict) -> dict:
        return self.policy_model.stat(**query)