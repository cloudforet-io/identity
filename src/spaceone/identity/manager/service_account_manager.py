import logging

from spaceone.core.error import *
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.identity.model.service_account_model import ServiceAccount

_LOGGER = logging.getLogger(__name__)


class ServiceAccountManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_account_model: ServiceAccount = self.locator.get_model('ServiceAccount')

    def create_service_account(self, params):
        def _rollback(service_account_vo):
            _LOGGER.info(f'[create_service_account._rollback] '
                         f'Create service_account : {service_account_vo.name} '
                         f'({service_account_vo.service_account_id})')
            service_account_vo.delete()

        service_account_vo: ServiceAccount = self.service_account_model.create(params)
        self.transaction.add_rollback(_rollback, service_account_vo)

        return service_account_vo

    def update_service_account(self, params):
        service_account_vo: ServiceAccount = self.get_service_account(params['service_account_id'],
                                                                      params['domain_id'])

        return self.update_service_account_by_vo(params, service_account_vo)

    def update_service_account_by_vo(self, params, service_account_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_service_account._rollback] Revert Data : '
                         f'{old_data["service_account_id"]}')
            service_account_vo.update(old_data)

        self.transaction.add_rollback(_rollback, service_account_vo.to_dict())

        return service_account_vo.update(params)

    def delete_service_account(self, service_account_id, domain_id):
        service_account_vo: ServiceAccount = self.get_service_account(service_account_id, domain_id)
        service_account_vo.delete()

    def get_service_account(self, service_account_id, domain_id, only=None):
        return self.service_account_model.get(service_account_id=service_account_id, domain_id=domain_id, only=only)

    def list_service_accounts(self, query={}):
        return self.service_account_model.query(**query)

    def stat_service_accounts(self, query):
        return self.service_account_model.stat(**query)

    def update_secret_project(self, service_account_id, project_id, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='secret')
        response = self._list_secrets(secret_connector, service_account_id, domain_id)
        secrets = response.get('results', [])

        for secret_info in secrets:
            secret_connector.dispatch('Secret.update', {
                'secret_id': secret_info['secret_id'],
                'project_id': project_id,
                'domain_id': domain_id
            })

    def release_secret_project(self, service_account_id, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='secret')
        response = self._list_secrets(secret_connector, service_account_id, domain_id)
        secrets = response.get('results', [])

        for secret_info in secrets:
            secret_connector.dispatch('Secret.update', {
                'secret_id': secret_info['secret_id'],
                'release_project': True,
                'domain_id': domain_id
            })

    def delete_service_account_secrets(self, service_account_id, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='secret')
        response = self._list_secrets(secret_connector, service_account_id, domain_id)
        for secret_info in response.get('results', []):
            secret_connector.dispatch('Secret.delete', {
                'secret_id': secret_info['secret_id'],
                'domain_id': domain_id
            })

    def check_service_account_secrets(self, service_account_id, domain_id):
        secret_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='secret')
        response = self._list_secrets(secret_connector, service_account_id, domain_id)
        total_count = response.get('total_count', 0)

        if total_count > 0:
            raise ERROR_EXIST_RESOURCE(parent='ServiceAccount', child='Secret')

    @staticmethod
    def _list_secrets(secret_connector, service_account_id, domain_id):
        return secret_connector.dispatch('Secret.list', {
            'service_account_id': service_account_id,
            'domain_id': domain_id
        })
