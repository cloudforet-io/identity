from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import workspace_user_pb2, workspace_user_pb2_grpc
from spaceone.identity.service.workspace_user_service import WorkspaceUserService


class WorkspaceUser(BaseAPI, workspace_user_pb2_grpc.WorkspaceUserServicer):
    pb2 = workspace_user_pb2
    pb2_grpc = workspace_user_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_user_svc = WorkspaceUserService(metadata)
        response: dict = workspace_user_svc.create(params)
        return self.dict_to_message(response)

    def find(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_user_svc = WorkspaceUserService(metadata)
        response: dict = workspace_user_svc.find(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_user_svc = WorkspaceUserService(metadata)
        response: dict = workspace_user_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_user_svc = WorkspaceUserService(metadata)
        response: dict = workspace_user_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_user_svc = WorkspaceUserService(metadata)
        response: dict = workspace_user_svc.stat(params)
        return self.dict_to_message(response)
