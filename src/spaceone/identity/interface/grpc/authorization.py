from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import authorization_pb2, authorization_pb2_grpc
from spaceone.identity.service.authorization_service import AuthorizationService


class Authorization(BaseAPI, authorization_pb2_grpc.AuthorizationServicer):
    pb2 = authorization_pb2
    pb2_grpc = authorization_pb2_grpc

    def verify(self, request, context):
        params, metadata = self.parse_request(request, context)
        authorization_svc = AuthorizationService(metadata)
        response: dict = authorization_svc.verify(params)
        return self.dict_to_message(response)
