from spaceone.api.identity.v2 import workspace_group_pb2, workspace_group_pb2_grpc
from spaceone.core.pygrpc import BaseAPI

from spaceone.identity.service.workspace_group_service import WorkspaceGroupService


class WorkspaceGroup(BaseAPI, workspace_group_pb2_grpc.WorkspaceGroupServicer):
    pb2 = workspace_group_pb2
    pb2_grpc = workspace_group_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        workspace_group_svc.delete(params)
        return self.empty()

    def add_workspaces(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.add_workspaces(params)
        return self.dict_to_message(response)

    def remove_workspaces(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.remove_workspaces(params)
        return self.dict_to_message(response)

    def find_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.find_users(params)
        return self.dict_to_message(response)

    def add_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.add_users(params)
        return self.dict_to_message(response)

    def remove_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.remove_users(params)
        return self.dict_to_message(response)

    def update_role(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.update_role(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_svc = WorkspaceGroupService(metadata)
        response: dict = workspace_group_svc.stat(params)
        return self.dict_to_message(response)
