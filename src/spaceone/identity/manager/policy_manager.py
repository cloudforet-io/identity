import logging
from datetime import datetime

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.error.error_role import *
from spaceone.identity.model.policy_model import Policy
from spaceone.identity.manager.role_manager import RoleManager
from spaceone.identity.connector.repository_connector import RepositoryConnector

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

        params['updated_at'] = datetime.utcnow()
        policy_vo = policy_vo.update(params)

        if 'permissions' in params:
            self._delete_role_cache(policy_vo)

        return policy_vo

    def delete_policy(self, policy_id, domain_id):
        policy_vo: Policy = self.get_policy(policy_id, domain_id)
        role_vos = self._get_roles_using_policy(policy_vo)

        for role_vo in role_vos:
            raise ERROR_POLICY_IS_IN_USE(policy_id=policy_id, role_id=role_vo.role_id)

        policy_vo.delete()

    def get_policy(self, policy_id, domain_id, only=None):
        return self.policy_model.get(policy_id=policy_id, domain_id=domain_id, policy_type='CUSTOM', only=only)

    def list_policies(self, query):
        return self.policy_model.query(**query)

    def stat_policies(self, query):
        return self.policy_model.stat(**query)

    def get_managed_policy(self, policy_id, domain_id):
        repo_managed_policy_info = self._get_managed_policy_from_repository(policy_id, domain_id)
        local_managed_policy_vo = self._get_managed_policy_from_local(policy_id, domain_id)

        if repo_managed_policy_info:
            if local_managed_policy_vo:
                if repo_managed_policy_info.get('updated_at') == local_managed_policy_vo.updated_at:
                    return local_managed_policy_vo

                return self._update_managed_policy(local_managed_policy_vo, repo_managed_policy_info)

            return self._create_managed_policy(policy_id, domain_id, repo_managed_policy_info)
        else:
            if local_managed_policy_vo:
                return local_managed_policy_vo

            raise ERROR_NOT_FOUND(key='policy_id', value=policy_id)

    def _create_managed_policy(self, policy_id, domain_id, repo_managed_policy_info):
        policy_vo: Policy = self.create_policy({
            'policy_id': policy_id,
            'name': repo_managed_policy_info['name'],
            'policy_type': 'MANAGED',
            'permissions': repo_managed_policy_info.get('permissions', []),
            'tags': repo_managed_policy_info.get('tags', []),
            'domain_id': domain_id,
            'updated_at': repo_managed_policy_info.get('updated_at')
        })

        return policy_vo

    def _update_managed_policy(self, local_managed_policy_vo, repo_managed_policy_info):
        policy_vo: Policy = local_managed_policy_vo.update({
            'name': repo_managed_policy_info['name'],
            'permissions': repo_managed_policy_info.get('permissions', []),
            'tags': repo_managed_policy_info.get('tags', []),
            'updated_at': repo_managed_policy_info.get('updated_at')
        })

        self._delete_role_cache(policy_vo)

        return policy_vo

    @cache.cacheable(key='managed-policy:{domain_id}:{policy_id}', expire=600)
    def _get_managed_policy_from_repository(self, policy_id, domain_id):
        repo_connector: RepositoryConnector = self.locator.get_connector('RepositoryConnector')
        try:
            return repo_connector.get_policy(policy_id, domain_id)
        except Exception as e:
            _LOGGER.error(f'Failed to get managed policy. (policy_id = {policy_id})')
            return None

    def _get_managed_policy_from_local(self, policy_id, domain_id):
        managed_policy_vos = self.policy_model.filter(policy_id=policy_id, policy_type='MANAGED', domain_id=domain_id)
        if managed_policy_vos.count() > 0:
            return managed_policy_vos[0]
        else:
            return None

    def _delete_role_cache(self, policy_vo):
        role_vos = self._get_roles_using_policy(policy_vo)
        for role_vo in role_vos:
            cache.delete_pattern(f'role-permissions:{role_vo.domain_id}:{role_vo.role_id}')
            cache.delete_pattern(f'user-permissions:{role_vo.domain_id}:*{role_vo.role_id}*')

    def _get_roles_using_policy(self, policy_vo):
        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        query = {
            'filter': [
                {
                    'k': 'policies.policy',
                    'v': policy_vo,
                    'o': 'eq'
                }
            ]
        }

        role_vos, total_count = role_mgr.list_roles(query)
        return role_vos
