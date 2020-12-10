from spaceone.api.identity.v1 import service_account_pb2, service_account_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class ServiceAccount(BaseAPI, service_account_pb2_grpc.ServiceAccountServicer):

    pb2 = service_account_pb2
    pb2_grpc = service_account_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ServiceAccountService', metadata) as service_account_svc:
            data = service_account_svc.create(params)
            return self.locator.get_info('ServiceAccountInfo', data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ServiceAccountService', metadata) as service_account_svc:
            data = service_account_svc.update(params)
            return self.locator.get_info('ServiceAccountInfo', data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ServiceAccountService', metadata) as service_account_svc:
            service_account_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ServiceAccountService', metadata) as service_account_svc:
            data = service_account_svc.get(params)
            return self.locator.get_info('ServiceAccountInfo', data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ServiceAccountService', metadata) as service_account_svc:
            service_account_vos, total_count = service_account_svc.list(params)
            return self.locator.get_info('ServiceAccountsInfo', service_account_vos,
                                         total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ServiceAccountService', metadata) as service_account_svc:
            return self.locator.get_info('StatisticsInfo', service_account_svc.stat(params))
