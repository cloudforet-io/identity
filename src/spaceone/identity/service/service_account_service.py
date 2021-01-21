from jsonschema import validate

from spaceone.core.service import *
from spaceone.core.error import *
from spaceone.identity.manager.service_account_manager import ServiceAccountManager
from spaceone.identity.manager.project_manager import ProjectManager
from spaceone.identity.manager.provider_manager import ProviderManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ServiceAccountService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_account_mgr: ServiceAccountManager = self.locator.get_manager('ServiceAccountManager')

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['name', 'data', 'provider', 'domain_id'])
    def create(self, params):
        """
        Args:
            params (dict): {
                'name': 'str',
                'data': 'dict',
                'provider': 'str',
                'project_id': 'str',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            service_account_vo (object)
        """

        self._check_data(params['data'], params['provider'])

        if 'project_id' in params:
            params['project'] = self._get_project(params['project_id'], params['domain_id'])

        return self.service_account_mgr.create_service_account(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['service_account_id', 'domain_id'])
    def update(self, params):
        """
        Args:
            params (dict): {
                'service_account_id': 'str',
                'name': 'str',
                'data': 'dict',
                'project_id': 'str',
                'tags': 'list',
                'release_project': 'bool',
                'domain_id': 'str'
            }

        Returns:
            service_account_vo (object)
        """

        service_account_id = params['service_account_id']
        domain_id = params['domain_id']
        project_id = params.get('project_id')
        release_project = params.get('release_project')

        service_account_vo = self.service_account_mgr.get_service_account(service_account_id, domain_id)

        if 'data' in params:
            self._check_data(params['data'], service_account_vo.provider)

        if release_project:
            params['project'] = None
            params['project_id'] = None
        elif project_id:
            params['project'] = self._get_project(params['project_id'], params['domain_id'])

        service_account_vo = self.service_account_mgr.update_service_account_by_vo(params, service_account_vo)

        if release_project:
            self.service_account_mgr.release_secret_project(service_account_id, domain_id)
        elif project_id:
            self.service_account_mgr.update_secret_project(service_account_id, project_id, domain_id)

        return service_account_vo

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['service_account_id', 'domain_id'])
    def delete(self, params):
        """
        Args:
            params (dict): {
                'service_account_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        service_account_id = params['service_account_id']
        domain_id = params['domain_id']

        # self.service_account_mgr.check_service_account_secrets(service_account_id, domain_id)
        self.service_account_mgr.delete_service_account_secrets(service_account_id, domain_id)
        self.service_account_mgr.delete_service_account(service_account_id, domain_id)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['service_account_id', 'domain_id'])
    @change_only_key({'project_info': 'project'})
    def get(self, params):
        """
        Args:
            params (dict): {
                'service_account_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            service_account_vo (object)
        """

        return self.service_account_mgr.get_service_account(params['service_account_id'], params['domain_id'],
                                                            params.get('only'))

    @transaction(append_meta={'authorization.scope': 'PROJECT',
                              'mutation.append_parameter': {'project_id': 'authorization.projects'}})
    @check_required(['domain_id'])
    @change_only_key({'project_info': 'project'}, key_path='query.only')
    @append_query_filter(['service_account_id', 'name', 'provider', 'project_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['service_account_id', 'name', 'provider'])
    def list(self, params):
        """
        Args:
            params (dict): {
                    'service_account_id': 'str',
                    'name': 'str',
                    'provider': 'str',
                    'project_id': 'str',
                    'domain_id': 'str',
                    'query': 'dict (spaceone.api.core.v1.Query)'
                }

        Returns:
            results (list): 'list of service_account_vo'
            total_count (int)
        """
        query = params.get('query', {})

        # Temporary code for DB migration
        if 'only' in query:
            query['only'] += ['project_id']

        return self.service_account_mgr.list_service_accounts(query)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['service_account_id', 'name', 'provider'])
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
        return self.service_account_mgr.stat_service_accounts(query)

    def _check_data(self, data, provider):
        provider_mgr: ProviderManager = self.locator.get_manager('ProviderManager')
        provider_vo = provider_mgr.get_provider(provider)
        schema = provider_vo.template.get('service_account', {}).get('schema', [])
        try:
            validate(instance=data, schema=schema)
        except Exception as e:
            raise ERROR_INVALID_PARAMETER(key='data', reason=e.message)

    def _get_project(self, project_id, domain_id):
        project_mgr: ProjectManager = self.locator.get_manager('ProjectManager')
        return project_mgr.get_project(project_id, domain_id)
