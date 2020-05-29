from spaceone.api.identity.v1 import policy_pb2, policy_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Policy(BaseAPI, policy_pb2_grpc.PolicyServicer):

    pb2 = policy_pb2
    pb2_grpc = policy_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            data = policy_svc.create_policy(params)
            return self.locator.get_info('PolicyInfo', data)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            data = policy_svc.update_policy(params)
            return self.locator.get_info('PolicyInfo', data)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            policy_svc.delete_policy(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            data = policy_svc.get_policy(params)
            return self.locator.get_info('PolicyInfo', data)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            policy_vos, total_count = policy_svc.list_policies(params)
            return self.locator.get_info('PoliciesInfo', policy_vos, total_count, minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PolicyService', metadata) as policy_svc:
            return self.locator.get_info('StatisticsInfo', policy_svc.stat(params))
