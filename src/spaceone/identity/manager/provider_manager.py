import logging

from spaceone.core.manager import BaseManager
from spaceone.identity.conf.provider_conf import DEFAULT_PROVIDERS
from spaceone.identity.model.provider_model import Provider

_LOGGER = logging.getLogger(__name__)


class ProviderManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_model: Provider = self.locator.get_model('Provider')

    def create_provider(self, params):
        def _rollback(provider_vo):
            _LOGGER.info(f'[create_provider._rollback] Create provider : {provider_vo.provider}')
            provider_vo.delete()

        provider_vo: Provider = self.provider_model.create(params)
        self.transaction.add_rollback(_rollback, provider_vo)

        return provider_vo

    def update_provider(self, params):
        def _rollback(old_data):
            _LOGGER.info(f'[update_provider._rollback] Revert Data : {old_data["provider"]}')
            provider_vo.update(old_data)

        provider_vo: Provider = self.get_provider(params['provider'], params['domain_id'])
        self.transaction.add_rollback(_rollback, provider_vo.to_dict())

        return provider_vo.update(params)

    def delete_provider(self, provider, domain_id):
        provider_vo: Provider = self.get_provider(provider, domain_id)
        provider_vo.delete()

    def get_provider(self, provider, domain_id, only=None):
        return self.provider_model.get(provider=provider, domain_id=domain_id, only=only)

    def filter_providers(self, **conditions):
        return self.provider_model.filter(**conditions)

    def list_providers(self, query={}):
        return self.provider_model.query(**query)

    def stat_providers(self, query):
        return self.provider_model.stat(**query)

    def create_default_providers(self, installed_providers, domain_id):
        for provider in DEFAULT_PROVIDERS:
            if provider['provider'] not in installed_providers:
                _LOGGER.debug(f'Create default provider: {provider["name"]}')
                provider['domain_id'] = domain_id
                self.create_provider(provider)
