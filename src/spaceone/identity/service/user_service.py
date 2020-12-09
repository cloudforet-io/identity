from spaceone.core.service import *
from spaceone.identity.error.error_user import *
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
    def create(self, params):
        """ Create user

        Args:
            params (dict): {
                'user_id': 'str',
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'user_type': 'str',
                'backend': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            user_vo (object)
        """

        params['user_type'] = params.get('user_type', 'USER')
        params['backend'] = params.get('backend', 'LOCAL')
        domain_id = params['domain_id']

        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        domain_vo: Domain = domain_mgr.get_domain(domain_id)

        self._check_user_type_and_backend(params['user_type'], params['backend'], domain_vo)

        return self.user_mgr.create_user(params, domain_vo)

    @transaction
    @check_required(['user_id', 'domain_id'])
    def update(self, params):
        """ Update user

        Args:
            params (dict): {
                'user_id': 'str',
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'language': 'str',
                'timezone': 'str',
                'tags': 'list',
                'domain_id': 'str'
            }

        Returns:
            user_vo (object)
        """

        return self.user_mgr.update_user(params)

    @transaction
    @check_required(['user_id', 'domain_id'])
    def enable(self, params):
        """ Enable user

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            user_vo (object)
        """

        return self.user_mgr.enable_user(params['user_id'], params['domain_id'])

    @transaction
    @check_required(['user_id', 'domain_id'])
    def disable(self, params):
        """ Disable user

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            user_vo (object)
        """

        return self.user_mgr.disable_user(params['user_id'], params['domain_id'])

    @transaction
    @check_required(['user_id', 'domain_id'])
    def delete(self, params):
        """ Delete user

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        return self.user_mgr.delete_user(params['user_id'], params['domain_id'])

    @transaction
    @check_required(['search', 'domain_id'])
    def find(self, params):
        """ Disable user

        Args:
            params (dict): {
                'search' (one of): {
                    'user_id': 'str',
                    'keyword': 'str'
                },
                'domain_id': 'str'
            }

        Returns:
            results(list) : 'list of {
                                'user_id': 'str',
                                'name': 'str',
                                'email': 'str',
                                'tags': 'list'
                            }'
        """

        if not any(k in params['search'] for k in ['keyword', 'user_id']):
            raise ERROR_REQUIRED_PARAMETER(key='search.keyword | search.user_id')

        domain_mgr: DomainManager = self.locator.get_manager('DomainManager')
        domain_vo: Domain = domain_mgr.get_domain(params['domain_id'])

        # Check External Authentication from Domain
        if not domain_vo.plugin_info:
            raise ERROR_NOT_ALLOWED_EXTERNAL_AUTHENTICATION()

        return self.user_mgr.find_user(params['search'], domain_vo)

    @transaction
    @check_required(['user_id', 'roles', 'domain_id'])
    def update_role(self, params):
        """ Update user role

        Args:
            params (dict): {
                'user_id': 'str',
                'roles': 'list',
                'domain_id': 'str'
            }

        Returns:
            user_vo (object)
        """

        role_vos = self._get_roles(params['roles'], params['domain_id'])
        self._check_role_type(role_vos)

        return self.user_mgr.update_role(params, role_vos)

    @transaction
    @check_required(['user_id', 'domain_id'])
    def get(self, params):
        """ Get user

        Args:
            params (dict): {
                'user_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            user_vo (object)
        """

        return self.user_mgr.get_user(params['user_id'], params['domain_id'], params.get('only'))

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['user_id', 'name', 'state', 'email', 'user_type', 'backend', 'role_id', 'domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['user_id', 'name', 'email'])
    def list(self, params):
        """ List users

        Args:
            params (dict): {
                'user_id': 'str',
                'name': 'str',
                'state': 'str',
                'email': 'str',
                'user_type': 'str',
                'backend': 'str',
                'role_id': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)'
            }

        Returns:
            results (list): 'list of user_vo'
            total_count (int)
        """

        query: dict = params.get('query', {})
        return self.user_mgr.list_users(query)

    @transaction
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id'])
    @change_tag_filter('tags')
    @append_keyword_filter(['user_id', 'name', 'email'])
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
        return self.user_mgr.stat_users(query)

    @staticmethod
    def _check_user_type_and_backend(user_type, backend, domain_vo):
        # Check User Type and Backend
        if user_type == 'API_USER':
            if backend == 'EXTERNAL':
                raise ERROR_EXTERNAL_USER_NOT_ALLOWED_API_USER()

        # Check External Authentication from Domain
        if backend == 'EXTERNAL':
            if not domain_vo.plugin_info:
                raise ERROR_NOT_ALLOWED_EXTERNAL_AUTHENTICATION()

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
