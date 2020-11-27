from spaceone.core.service import *
from spaceone.identity.manager.endpoint_manager import EndpointManager


@event_handler
class EndpointService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint_mgr: EndpointManager = self.locator.get_manager('EndpointManager')

    @transaction
    @check_required(['domain_id'])
    @append_query_filter(['service'])
    @append_keyword_filter(['service'])
    def list_endpoints(self, params):
        """
        Args:
            params (dict): {
                    'query': 'dict (spaceone.api.core.v1.Query)',
                    'service': 'str',
                    'domain_id': 'str'
                }

        Returns:
            results (list)
            total_count (int)

        """
        return self.endpoint_mgr.list_endpoints(params.get('query', {}))
