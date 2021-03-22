from spaceone.core import cache
from spaceone.core.service import *
from spaceone.core import utils
from spaceone.identity.manager.provider_manager import ProviderManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProviderService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_mgr: ProviderManager = self.locator.get_manager('ProviderManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['provider', 'name', 'domain_id'])
    def create(self, params):
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

        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return self.provider_mgr.create_provider(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['provider', 'domain_id'])
    def update(self, params):
        """
        Args:
            params (dict): {
                'provider': 'str',
                'name': 'str',
                'template': 'dict',
                'metadata': 'dict',
                'capability': 'dict',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            provider_vo (object)
        """
        # TODO: validate a template data
        # TODO: validate a capability data
        
        if 'tags' in params:
            params['tags'] = utils.dict_to_tags(params['tags'])

        return self.provider_mgr.update_provider(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['provider', 'domain_id'])
    def delete(self, params):
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

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['provider', 'domain_id'])
    def get(self, params):
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

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['provider', 'name'])
    @change_tag_filter('tags')
    @append_keyword_filter(['provider', 'name'])
    def list(self, params):
        """
        Args:
            params (dict): {
                    'query': 'dict (spaceone.api.core.v1.Query)',
                    'provider': 'str',
                    'name': 'str',
                    'domain_id': 'str'
                }

        Returns:
            results (list): 'list of provider_vo'
            total_count (int)
        """
        self._create_default_provider()
        return self.provider_mgr.list_providers(params.get('query', {}))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['provider', 'name'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'domain_id': 'str'
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get('query', {})
        return self.provider_mgr.stat_providers(query)

    @cache.cacheable(key='provider:default:init', expire=300)
    def _create_default_provider(self):
        provider_vos, total_count = self.provider_mgr.list_providers()
        installed_providers = [provider_vo.provider for provider_vo in provider_vos]
        self.provider_mgr.create_default_providers(installed_providers)

        return True
