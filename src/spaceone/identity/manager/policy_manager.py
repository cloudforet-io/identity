import logging

from spaceone.core.manager import BaseManager
from spaceone.identity.model.policy_model import Policy

_LOGGER = logging.getLogger(__name__)


class PolicyManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_model: Policy = self.locator.get_model('Policy')

    def create_policy(self, params):
        def _rollback(policy_vo):
            _LOGGER.info(f'[create_policy._rollback] Create policy : {policy_vo.name} ({policy_vo.policy_id})')
            policy_vo.delete()

        policy_vo: Policy = self.policy_model.create(params)
        self.transaction.add_rollback(_rollback, policy_vo)

        return policy_vo

    def update_policy(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_policy._rollback] Revert Data : {old_data["name"]} ({old_data["policy_id"]})')
            policy_vo.update(old_data)

        policy_vo: Policy = self.get_policy(params['policy_id'], params['domain_id'])
        self.transaction.add_rollback(_rollback, policy_vo.to_dict())

        policy_vo = policy_vo.update(params)
        return policy_vo

    def delete_policy(self, policy_id, domain_id):
        policy_vo: Policy = self.get_policy(policy_id, domain_id)
        policy_vo.delete()

    def get_policy(self, policy_id, domain_id, only=None):
        return self.policy_model.get(policy_id=policy_id, domain_id=domain_id, only=only)

    def list_policies(self, query):
        return self.policy_model.query(**query)

    def stat_policies(self, query):
        return self.policy_model.stat(**query)
