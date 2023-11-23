from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import external_auth_pb2, external_auth_pb2_grpc
from spaceone.identity.service.external_auth_service import ExternalAuthService


class ExternalAuth(BaseAPI, external_auth_pb2_grpc.ExternalAuthServicer):
    pb2 = external_auth_pb2
    pb2_grpc = external_auth_pb2_grpc

    def set(self, request, context):
        params, metadata = self.parse_request(request, context)
        external_auth_svc = ExternalAuthService(metadata)
        response: dict = external_auth_svc.set(params)
        return self.dict_to_message(response)

    def unset(self, request, context):
        params, metadata = self.parse_request(request, context)
        external_auth_svc = ExternalAuthService(metadata)
        response: dict = external_auth_svc.unset(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        external_auth_svc = ExternalAuthService(metadata)
        response: dict = external_auth_svc.get(params)
        return self.dict_to_message(response)
