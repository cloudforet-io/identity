from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.plugin import (
    external_auth_pb2,
    external_auth_pb2_grpc,
)
from spaceone.identity.plugin.external_auth.service.external_auth_service import (
    ExternalAuthService,
)


class ExternalAuth(BaseAPI, external_auth_pb2_grpc.ExternalAuthServicer):
    pb2 = external_auth_pb2
    pb2_grpc = external_auth_pb2_grpc

    def init(self, request, context):
        params, metadata = self.parse_request(request, context)
        external_auth_svc = ExternalAuthService(metadata)
        response: dict = external_auth_svc.init(params)
        return self.dict_to_message(response)

    def authorize(self, request, context):
        params, metadata = self.parse_request(request, context)
        external_auth_svc = ExternalAuthService(metadata)
        response: dict = external_auth_svc.authorize(params)
        return self.dict_to_message(response)
