from spaceone.api.identity.v2 import (
    workspace_group_details_pb2,
    workspace_group_details_pb2_grpc,
)
from spaceone.core.pygrpc import BaseAPI

from spaceone.identity.service.workspace_group_details_service import (
    WorkspaceGroupDetailsService,
)


class WorkspaceGroupDetails(
    BaseAPI, workspace_group_details_pb2_grpc.WorkspaceGroupDetailsServicer
):
    pb2 = workspace_group_details_pb2
    pb2_grpc = workspace_group_details_pb2_grpc

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        response: dict = workspace_group_details_svc.update(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        workspace_group_details_svc.delete(params)
        return self.empty()

    def add_workspaces(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        response: dict = workspace_group_details_svc.add_workspaces(params)
        return self.dict_to_message(response)

    def remove_workspaces(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        response: dict = workspace_group_details_svc.remove_workspaces(params)
        return self.dict_to_message(response)

    def find_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        response: dict = workspace_group_details_svc.find_users(params)
        return self.dict_to_message(response)

    def add_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        response: dict = workspace_group_details_svc.add_users(params)
        return self.dict_to_message(response)

    def remove_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        response: dict = workspace_group_details_svc.remove_users(params)
        return self.dict_to_message(response)

    def get_workspace_groups(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_details_svc = WorkspaceGroupDetailsService(metadata)
        response: dict = workspace_group_details_svc.get_workspace_groups(params)
        return self.dict_to_message(response)
