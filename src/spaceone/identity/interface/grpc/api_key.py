from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import api_key_pb2, api_key_pb2_grpc
from spaceone.identity.service.api_key_service import APIKeyService


class APIKey(BaseAPI, api_key_pb2_grpc.APIKeyServicer):
    pb2 = api_key_pb2
    pb2_grpc = api_key_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        response: dict = api_key_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        response: dict = api_key_svc.update(params)
        return self.dict_to_message(response)

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        response: dict = api_key_svc.enable(params)
        return self.dict_to_message(response)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        response: dict = api_key_svc.disable(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        api_key_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        response: dict = api_key_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        response: dict = api_key_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        api_key_svc = APIKeyService(metadata)
        response: dict = api_key_svc.stat(params)
        return self.dict_to_message(response)
