from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import agent_pb2, agent_pb2_grpc
from spaceone.identity.service.agent_service import (
    AgentService,
)


class Agent(BaseAPI, agent_pb2_grpc.AgentServicer):
    pb2 = agent_pb2
    pb2_grpc = agent_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        agent_svc = AgentService(metadata)
        response: dict = agent_svc.create(params)
        return self.dict_to_message(response)

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        agent_svc = AgentService(metadata)
        response: dict = agent_svc.enable(params)
        return self.dict_to_message(response)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        agent_svc = AgentService(metadata)
        response: dict = agent_svc.disable(params)
        return self.dict_to_message(response)

    def regenerate(self, request, context):
        params, metadata = self.parse_request(request, context)
        agent_svc = AgentService(metadata)
        response: dict = agent_svc.regenerate(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        agent_svc = AgentService(metadata)
        agent_svc.delete(params)
        return self.empty()

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        agent_svc = AgentService(metadata)
        response: dict = agent_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        agent_svc = AgentService(metadata)
        response: dict = agent_svc.list(params)
        return self.dict_to_message(response)
