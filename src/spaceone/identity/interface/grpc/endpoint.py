from spaceone.api.identity.v1 import endpoint_pb2, endpoint_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Endpoint(BaseAPI, endpoint_pb2_grpc.EndpointServicer):

    pb2 = endpoint_pb2
    pb2_grpc = endpoint_pb2_grpc

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('EndpointService', metadata) as endpoint_svc:
            endpoint_vos, total_count = endpoint_svc.list(params)
            return self.locator.get_info('EndpointsInfo', endpoint_vos,
                                         total_count, minimal=self.get_minimal(params))
