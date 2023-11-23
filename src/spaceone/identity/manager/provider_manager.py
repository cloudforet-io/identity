import logging
from jsonschema import validate, exceptions
from typing import Tuple, List

from spaceone.core.manager import BaseManager
from spaceone.core.error import *
from spaceone.identity.conf.provider_conf import DEFAULT_PROVIDERS
from spaceone.identity.model.provider.database import Provider

_LOGGER = logging.getLogger(__name__)


class ProviderManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_model = Provider

    def create_provider(self, params: dict) -> Provider:
        def _rollback(vo: Provider):
            _LOGGER.info(f'[create_provider._rollback] Delete provider : {vo.provider}')
            vo.delete()

        provider_vo = self.provider_model.create(params)
        self.transaction.add_rollback(_rollback, provider_vo)

        return provider_vo

    def update_provider_by_vo(
        self, params: dict, provider_vo: Provider
    ) -> Provider:
        def _rollback(old_data):
            _LOGGER.info(f'[update_provider._rollback] Revert Data : {old_data["provider"]}')
            provider_vo.update(old_data)

        self.transaction.add_rollback(_rollback, provider_vo.to_dict())

        return provider_vo.update(params)

    @staticmethod
    def delete_provider_by_vo(provider_vo: Provider) -> None:
        provider_vo.delete()

    def get_provider(self, provider: str, domain_id: str) -> Provider:
        return self.provider_model.get(provider=provider, domain_id=domain_id)

    def filter_providers(self, **conditions) -> List[Provider]:
        return self.provider_model.filter(**conditions)

    def list_providers(self, query: dict) -> Tuple[list, int]:
        return self.provider_model.query(**query)

    def stat_providers(self, query: dict) -> dict:
        return self.provider_model.stat(**query)

    def create_default_providers(self, installed_providers: List[str], domain_id: str) -> None:
        for provider in DEFAULT_PROVIDERS:
            if provider['provider'] not in installed_providers:
                _LOGGER.debug(f'Create default provider: {provider["name"]}')
                provider['domain_id'] = domain_id
                self.create_provider(provider)

    def check_data_by_schema(self, provider: str, domain_id: str, data: dict) -> None:
        provider_vo = self.get_provider(provider, domain_id)
        schema = provider_vo.template.get('service_account', {}).get('schema')

        if schema:
            try:
                validate(instance=data, schema=schema)
            except exceptions.ValidationError as e:
                raise ERROR_INVALID_PARAMETER(key='data', reason=e.message)
