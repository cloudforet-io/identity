from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import policy_pb2, policy_pb2_grpc
from spaceone.identity.service.policy_service import PolicyService


class Policy(BaseAPI, policy_pb2_grpc.PolicyServicer):
    pb2 = policy_pb2
    pb2_grpc = policy_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        policy_svc = PolicyService(metadata)
        response: dict = policy_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        policy_svc = PolicyService(metadata)
        response: dict = policy_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        policy_svc = PolicyService(metadata)
        policy_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        policy_svc = PolicyService(metadata)
        response: dict = policy_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        policy_svc = PolicyService(metadata)
        response: dict = policy_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        policy_svc = PolicyService(metadata)
        response: dict = policy_svc.stat(params)
        return self.dict_to_message(response)
