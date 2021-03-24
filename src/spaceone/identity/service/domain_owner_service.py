import pytz
from spaceone.core.service import *
from spaceone.core.error import *
from spaceone.identity.manager import DomainOwnerManager


@authentication_handler(exclude=['create'])
@authorization_handler(exclude=['create'])
@mutation_handler(exclude=['create'])
@event_handler
class DomainOwnerService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.domain_owner_mgr: DomainOwnerManager = self.locator.get_manager('DomainOwnerManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['owner_id', 'password', 'domain_id'])
    def create(self, params):
        """ Create domain owner

        Args:
            params (dict): {
                'owner_id': 'str',
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'language': 'str',
                'timezone': 'str',
                'domain_id': 'str'
            }

        Returns:
            domain_owner_vo (object)
        """

        if 'timezone' in params:
            self._check_timezone(params['timezone'])

        return self.domain_owner_mgr.create_owner(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['owner_id', 'domain_id'])
    def update(self, params):
        """ Update domain owner

        Args:
            params (dict): {
                'owner_id': 'str',
                'password': 'str',
                'name': 'str',
                'email': 'str',
                'language': 'str',
                'timezone': 'str',
                'domain_id': 'str'
            }

        Returns:
            domain_owner_vo (object)
        """

        if 'timezone' in params:
            self._check_timezone(params['timezone'])

        return self.domain_owner_mgr.update_owner(params)

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id', 'owner_id'])
    def delete(self, params):
        """ Delete domain owner

        Args:
            params (dict): {
                'owner_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """
        self.domain_owner_mgr.delete_owner(params['domain_id'], params['owner_id'])

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @check_required(['domain_id'])
    def get(self, params):
        """ Delete domain owner

        Args:
            params (dict): {
                'owner_id': 'str',
                'domain_id': 'str',
                'only': 'list'
            }

        Returns:
            domain_owner_vo (object)
        """
        return self.domain_owner_mgr.get_owner(params['domain_id'], params.get('owner_id'), params.get('only'))

    @staticmethod
    def _check_timezone(timezone):
        if timezone not in pytz.all_timezones:
            raise ERROR_INVALID_PARAMETER(key='timezone', reason='Timezone is invalid.')
