from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.plugin import (
    account_collector_pb2,
    account_collector_pb2_grpc,
)
from spaceone.identity.plugin.account_collector.service.account_collector_service import (
    AccountCollectorService,
)


class AccountCollector(BaseAPI, account_collector_pb2_grpc.AccountCollectorServicer):
    pb2 = account_collector_pb2
    pb2_grpc = account_collector_pb2_grpc

    def init(self, request, context):
        params, metadata = self.parse_request(request, context)
        account_collector_svc = AccountCollectorService(metadata)
        response: dict = account_collector_svc.init(params)
        return self.dict_to_message(response)

    def sync(self, request, context):
        params, metadata = self.parse_request(request, context)
        account_collector_svc = AccountCollectorService(metadata)
        response: dict = account_collector_svc.sync(params)
        return self.dict_to_message(response)
