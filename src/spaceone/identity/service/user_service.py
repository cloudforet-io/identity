from spaceone.core.service import *
from spaceone.identity.error.error_user import *
from spaceone.identity.error import ERROR_UNSUPPORTED_API
from spaceone.identity.error.error_user import ERROR_NOT_ALLOWED_ROLE_TYPE
from spaceone.identity.model import Domain
from spaceone.identity.manager import UserManager, RoleManager, DomainManager


@authentication_handler
@authorization_handler
@event_handler
class UserService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.user_mgr: UserManager = self.locator.get_manager('UserManager')

    @transaction
    @check_required(['user_id', 'domain_id'])
    def create_user(self, params):
        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        domain: Domain = domain_mgr.get_domain(params['domain_id'])

        return self.user_mgr.create_user(params, domain)

    @transaction
    @check_required(['user_id', 'domain_id'])
    def update_user(self, params):
        return self.user_mgr.update_user(params)

    @transaction
    @check_required(['user_id', 'domain_id'])
    def delete_user(self, params):
        return self.user_mgr.delete_user(params['user_id'], params['domain_id'])

    @transaction
    @check_required(['user_id', 'domain_id'])
    def enable_user(self, params):
        return self.user_mgr.enable_user(params['user_id'], params['domain_id'])

    @transaction
    @check_required(['user_id', 'domain_id'])
    def disable_user(self, params):
        return self.user_mgr.disable_user(params['user_id'], params['domain_id'])

    @transaction
    @check_required(['search', 'domain_id'])
    def find_user(self, params):
        if not any(k in params['search'] for k in ['keyword', 'user_id']):
            raise ERROR_REQUIRED_PARAMETER(key='search.keyword | search.user_id')

        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        domain_vo: Domain = domain_mgr.get_domain(params['domain_id'])

        if not domain_vo.plugin_info:
            raise ERROR_UNSUPPORTED_API(reason='Your domain does not use external authentication plugin.')

        return self.user_mgr.find_user(params['search'], domain_vo)

    @transaction
    @check_required(['user_id', 'roles', 'domain_id'])
    def update_role(self, params):
        role_vos = self._get_roles(params['roles'], params['domain_id'])
        self._check_role_type(role_vos)

        return self.user_mgr.update_role(params, role_vos)

    @transaction
    @check_required(['user_id', 'domain_id'])
    def get_user(self, params):
        return self.user_mgr.get_user(params['user_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['user_id', 'name', 'state', 'email', 'mobile', 'group',
                          'role_id', 'domain_id'])
    @append_keyword_filter(['user_id', 'name', 'email', 'mobile', 'group'])
    def list_users(self, params):
        query: dict = params.get('query', {})
        return self.user_mgr.list_users(query)

    @transaction
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self.user_mgr.stat_users(query)

    @staticmethod
    def _check_role_type(role_vos):
        exist_domain_or_project_role = False
        exist_system_role = False

        for role_vo in role_vos:
            if role_vo.role_type in ['PROJECT', 'DOMAIN']:
                exist_domain_or_project_role = True
            elif role_vo.role_type == 'SYSTEM':
                exist_system_role = True

        if exist_domain_or_project_role and exist_system_role:
            raise ERROR_NOT_ALLOWED_ROLE_TYPE()

    def _get_roles(self, role_ids, domain_id):
        role_mgr: RoleManager = self.locator.get_manager('RoleManager')
        query = self._in_query(key='role_id', values=role_ids, domain_id=domain_id)
        role_vos, total_count = role_mgr.list_roles(query)

        if len(role_ids) != total_count:
            raise ERROR_NOT_FOUND(key='roles', value=str(role_ids))

        return role_vos

    @staticmethod
    def _in_query(key: str, values: list, domain_id: str):
        return {
            'filter': [
                {
                    'k': key,
                    'v': values,
                    'o': 'in'
                },
                {
                    'k': 'domain_id',
                    'v': domain_id,
                    'o': 'eq'
                }
            ]
        }
