from spaceone.core.service import *
from spaceone.identity.manager.endpoint_manager import EndpointManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class EndpointService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint_mgr: EndpointManager = self.locator.get_manager('EndpointManager')

    @transaction(append_meta={'authorization.scope': 'DOMAIN'})
    @append_query_filter(['service'])
    @append_keyword_filter(['service'])
    def list(self, params):
        """
        Args:
            params (dict): {
                    'query': 'dict (spaceone.api.core.v1.Query)',
                    'service': 'str',
                    'endpoint_type': 'str'
                }

        Returns:
            results (list): list of endpoint_vo
            total_count (int)
        """
        return self.endpoint_mgr.list_endpoints(params.get('query', {}), params.get('endpoint_type', 'public'))
