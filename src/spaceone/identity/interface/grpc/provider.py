from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import provider_pb2, provider_pb2_grpc
from spaceone.identity.service.provider_service import ProviderService


class Provider(BaseAPI, provider_pb2_grpc.ProviderServicer):
    pb2 = provider_pb2
    pb2_grpc = provider_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        provider_svc = ProviderService(metadata)
        response: dict = provider_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        provider_svc = ProviderService(metadata)
        response: dict = provider_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        service_account_svc = ProviderService(metadata)
        service_account_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        provider_svc = ProviderService(metadata)
        response: dict = provider_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        provider_svc = ProviderService(metadata)
        response: dict = provider_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        provider_svc = ProviderService(metadata)
        response: dict = provider_svc.stat(params)
        return self.dict_to_message(response)
