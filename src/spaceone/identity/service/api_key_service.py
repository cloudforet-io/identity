from spaceone.core.service import *
from spaceone.identity.manager import APIKeyManager, UserManager


@authentication_handler(exclude=['get'])
@authorization_handler(exclude=['get'])
@mutation_handler
@event_handler
class APIKeyService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.api_key_mgr: APIKeyManager = self.locator.get_manager('APIKeyManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['user_id', 'domain_id'])
    def create(self, params):
        """ Create api key

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            api_key_vo (object)
        """

        user_id = params['user_id']
        domain_id = params['domain_id']

        # Check user is exists.
        user_mgr: UserManager = self.locator.get_manager('UserManager')
        user_vo = user_mgr.get_user(user_id=user_id, domain_id=domain_id)

        return self.api_key_mgr.create_api_key(user_vo, domain_id)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['api_key_id', 'domain_id'])
    def enable(self, params):
        """ Enable api key

        Args:
            params (dict): {
                'api_key_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            api_key_vo (object)
        """

        return self.api_key_mgr.enable_api_key(params['api_key_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['api_key_id', 'domain_id'])
    def disable(self, params):
        """ Disable api key

        Args:
            params (dict): {
                'api_key_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            api_key_vo (object)
        """

        return self.api_key_mgr.disable_api_key(params['api_key_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['api_key_id', 'domain_id'])
    def delete(self, params):
        """ Delete api key

        Args:
            params (dict): {
                'api_key_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        self.api_key_mgr.delete_api_key(params['api_key_id'], params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['api_key_id', 'domain_id'])
    def get(self, params):
        """ Get api key

        Args:
            params (dict): {
                'api_key_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            api_key_vo (object)
        """

        return self.api_key_mgr.get_api_key(params['api_key_id'], params['domain_id'], params.get('only'))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    @append_query_filter(['api_key_id', 'state', 'user_id', 'domain_id'])
    @append_keyword_filter(['api_key_id', 'user_id'])
    def list(self, params):
        """ List api keys

        Args:
            params (dict): {
                'api_key_id': 'str',
                'state': 'str',
                'user_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of api_key_vo'
            total_count (int)
        """

        return self.api_key_mgr.list_api_keys(params.get('query', {}))

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @append_keyword_filter(['api_key_id', 'user_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get('query', {})
        return self.api_key_mgr.stat_api_keys(query)
