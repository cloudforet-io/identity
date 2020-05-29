from spaceone.api.identity.v1 import provider_pb2, provider_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Provider(BaseAPI, provider_pb2_grpc.ProviderServicer):

    pb2 = provider_pb2
    pb2_grpc = provider_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProviderService', metadata) as provider_svc:
            data = provider_svc.create_provider(params)
            return self.locator.get_info('ProviderInfo', data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProviderService', metadata) as provider_svc:
            data = provider_svc.update_provider(params)
            return self.locator.get_info('ProviderInfo', data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProviderService', metadata) as provider_svc:
            provider_svc.delete_provider(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProviderService', metadata) as provider_svc:
            data = provider_svc.get_provider(params)
            return self.locator.get_info('ProviderInfo', data)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProviderService', metadata) as provider_svc:
            return self.locator.get_info('StatisticsInfo', provider_svc.stat(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProviderService', metadata) as provider_svc:
            provider_vos, total_count = provider_svc.list_providers(params)
            return self.locator.get_info('ProvidersInfo', provider_vos,
                                         total_count, minimal=self.get_minimal(params))
