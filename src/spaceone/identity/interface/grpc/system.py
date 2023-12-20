from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import system_pb2, system_pb2_grpc
from spaceone.identity.service.system_service import SystemService


class System(BaseAPI, system_pb2_grpc.SystemServicer):
    pb2 = system_pb2
    pb2_grpc = system_pb2_grpc

    def init(self, request, context):
        params, metadata = self.parse_request(request, context)
        system_svc = SystemService(metadata)
        response: dict = system_svc.init(params)
        return self.dict_to_message(response)
