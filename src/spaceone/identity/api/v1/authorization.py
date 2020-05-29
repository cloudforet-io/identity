from spaceone.api.identity.v1 import authorization_pb2, authorization_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Authorization(BaseAPI, authorization_pb2_grpc.AuthorizationServicer):

    pb2 = authorization_pb2
    pb2_grpc = authorization_pb2_grpc

    def verify(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('AuthorizationService', metadata) as auth_service:
            auth_data = auth_service.verify(params)
            return self.locator.get_info('AuthorizationResponse', auth_data)

