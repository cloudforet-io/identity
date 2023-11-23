from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import role_binding_pb2, role_binding_pb2_grpc
from spaceone.identity.service.role_binding_service import RoleBindingService


class RoleBinding(BaseAPI, role_binding_pb2_grpc.RoleBindingServicer):
    pb2 = role_binding_pb2
    pb2_grpc = role_binding_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        role_binding_svc = RoleBindingService(metadata)
        response: dict = role_binding_svc.create(params)
        return self.dict_to_message(response)

    def update_role(self, request, context):
        params, metadata = self.parse_request(request, context)
        role_binding_svc = RoleBindingService(metadata)
        response: dict = role_binding_svc.update_role(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        role_binding_svc = RoleBindingService(metadata)
        role_binding_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        role_binding_svc = RoleBindingService(metadata)
        response: dict = role_binding_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        role_binding_svc = RoleBindingService(metadata)
        response: dict = role_binding_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        role_binding_svc = RoleBindingService(metadata)
        response: dict = role_binding_svc.stat(params)
        return self.dict_to_message(response)
