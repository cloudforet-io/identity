from spaceone.core import cache
from spaceone.core.service import *
from spaceone.identity.manager.provider_manager import ProviderManager


@authentication_handler
@authorization_handler
@event_handler
class ProviderService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_mgr: ProviderManager = self.locator.get_manager('ProviderManager')

    @transaction
    @check_required(['provider', 'name', 'domain_id'])
    def create_provider(self, params):
        """
        Args:
            params (dict): {
                'provider': 'str',
                'name': 'str',
                'template': 'dict',
                'metadata': 'dict',
                'capability': 'dict',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            provider_vo (object)

        """
        # TODO: validate a template data
        # TODO: validate a capability data
        return self.provider_mgr.create_provider(params)

    @transaction
    @check_required(['provider', 'domain_id'])
    def update_provider(self, params):
        """
        Args:
            params (dict): {
                'provider': 'str',
                'name': 'str',
                'template': 'dict',
                'metadata': 'dict',
                'capability': 'dict',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            provider_vo (object)

        """
        # TODO: validate a template data
        # TODO: validate a capability data
        return self.provider_mgr.update_provider(params)

    @transaction
    @check_required(['provider', 'domain_id'])
    def delete_provider(self, params):
        """
        Args:
            params (dict): {
                'provider': 'str',
                'domain_id': 'str'
            }

        Returns:
            None

        """
        self.provider_mgr.delete_provider(params['provider'])

    @transaction
    @check_required(['provider', 'domain_id'])
    def get_provider(self, params):
        """
        Args:
            params (dict): {
                'provider': 'str',
                'only': 'list',
                'domain_id': 'str'
            }

        Returns:
            provider_vo (object)

        """
        self._create_default_provider()
        return self.provider_mgr.get_provider(params['provider'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['provider', 'name'])
    @append_keyword_filter(['provider', 'name'])
    def list_providers(self, params):
        """
        Args:
            params (dict): {
                    'query': 'dict (spaceone.api.core.v1.Query)',
                    'provider': 'str',
                    'name': 'str',
                    'domain_id': 'str'
                }

        Returns:
            results (list)
            total_count (int)

        """
        self._create_default_provider()
        return self.provider_mgr.list_providers(params.get('query', {}))

    @transaction
    @check_required(['query', 'domain_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'domain_id': 'str'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self.provider_mgr.stat_providers(query)

    @cache.cacheable(key='provider:default:init', expire=300)
    def _create_default_provider(self):
        provider_vos, total_count = self.provider_mgr.list_providers()
        if total_count == 0:
            self.provider_mgr.create_default_providers()

        return True
