from spaceone.api.identity.v2 import workspace_pb2, workspace_pb2_grpc
from spaceone.core.pygrpc import BaseAPI

from spaceone.identity.service.workspace_service import WorkspaceService


class Workspace(BaseAPI, workspace_pb2_grpc.WorkspaceServicer):
    pb2 = workspace_pb2
    pb2_grpc = workspace_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.update(params)
        return self.dict_to_message(response)

    def change_workspace_group(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.change_workspace_group(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        workspace_svc.delete(params)
        return self.empty()

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.enable(params)
        return self.dict_to_message(response)

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.disable(params)
        return self.dict_to_message(response)

    def add_package(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.add_package(params)
        return self.dict_to_message(response)

    def remove_package(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.remove_package(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.get(params)
        return self.dict_to_message(response)

    def check(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        workspace_svc.check(params)
        return self.empty()

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.list(params)
        return self.dict_to_message(response)

    def analyze(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.analyze(params)
        return self.dict_to_message(response)


    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_svc = WorkspaceService(metadata)
        response: dict = workspace_svc.stat(params)
        return self.dict_to_message(response)
