from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import token_pb2, token_pb2_grpc
from spaceone.identity.service.token_service import TokenService


class Token(BaseAPI, token_pb2_grpc.TokenServicer):
    pb2 = token_pb2
    pb2_grpc = token_pb2_grpc

    def issue(self, request, context):
        params, metadata = self.parse_request(request, context)
        token_svc = TokenService(metadata)
        response: dict = token_svc.issue(params)
        return self.dict_to_message(response)

    def grant(self, request, context):
        params, metadata = self.parse_request(request, context)
        token_svc = TokenService(metadata)
        response: dict = token_svc.grant(params)
        return self.dict_to_message(response)
