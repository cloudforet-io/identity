from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import endpoint_pb2, endpoint_pb2_grpc
from spaceone.identity.service.endpoint_service import EndpointService


class Endpoint(BaseAPI, endpoint_pb2_grpc.EndpointServicer):
    pb2 = endpoint_pb2
    pb2_grpc = endpoint_pb2_grpc

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        endpoint_svc = EndpointService(metadata)
        response: dict = endpoint_svc.list(params)
        return self.dict_to_message(response)
