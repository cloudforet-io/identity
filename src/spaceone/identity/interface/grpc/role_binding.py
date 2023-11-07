from spaceone.api.identity.v1 import role_binding_pb2, role_binding_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class RoleBinding(BaseAPI, role_binding_pb2_grpc.RoleBindingServicer):

    pb2 = role_binding_pb2
    pb2_grpc = role_binding_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('RoleBindingService', metadata) as role_binding_svc:
            data = role_binding_svc.create(params)
            return self.locator.get_info('RoleBindingInfo', data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('RoleBindingService', metadata) as role_binding_svc:
            data = role_binding_svc.update(params)
            return self.locator.get_info('RoleBindingInfo', data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('RoleBindingService', metadata) as role_binding_svc:
            role_binding_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('RoleBindingService', metadata) as role_binding_svc:
            data = role_binding_svc.get(params)
            return self.locator.get_info('RoleBindingInfo', data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('RoleBindingService', metadata) as role_binding_svc:
            role_binding_vos, total_count = role_binding_svc.list(params)
            return self.locator.get_info('RoleBindingsInfo', role_binding_vos, total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('RoleBindingService', metadata) as role_binding_svc:
            return self.locator.get_info('StatisticsInfo', role_binding_svc.stat(params))
