from spaceone.api.identity.v1 import token_pb2, token_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Token(BaseAPI, token_pb2_grpc.TokenServicer):

    pb2 = token_pb2
    pb2_grpc = token_pb2_grpc

    def issue(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('TokenService', metadata) as token_svc:
            data = token_svc.issue(params)
            return self.locator.get_info('TokenInfo', data)

    def refresh(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('TokenService', metadata) as token_svc:
            data = token_svc.refresh(params)
            return self.locator.get_info('TokenInfo', data)
