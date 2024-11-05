from google.protobuf.json_format import ParseDict
from spaceone.api.identity.v2 import (
    workspace_group_pb2,
    workspace_group_user_pb2,
    workspace_group_user_pb2_grpc,
)
from spaceone.core.pygrpc import BaseAPI

from spaceone.identity.service.workspace_group_user_service import (
    WorkspaceGroupUserService,
)


class WorkspaceGroupUser(
    BaseAPI, workspace_group_user_pb2_grpc.WorkspaceGroupUserServicer
):
    pb2 = workspace_group_user_pb2
    pb2_grpc = workspace_group_user_pb2_grpc

    def add(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_user_svc = WorkspaceGroupUserService(metadata)
        response: dict = workspace_group_user_svc.add(params)
        return ParseDict(response, workspace_group_pb2.WorkspaceGroupInfo())

    def remove(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_user_svc = WorkspaceGroupUserService(metadata)
        response: dict = workspace_group_user_svc.remove(params)
        return ParseDict(response, workspace_group_pb2.WorkspaceGroupInfo())

    def update_role(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_user_svc = WorkspaceGroupUserService(metadata)
        response: dict = workspace_group_user_svc.update_role(params)
        return ParseDict(response, workspace_group_pb2.WorkspaceGroupInfo())

    def find(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_user_svc = WorkspaceGroupUserService(metadata)
        response: dict = workspace_group_user_svc.find(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_user_svc = WorkspaceGroupUserService(metadata)
        response: dict = workspace_group_user_svc.get(params)
        return ParseDict(response, workspace_group_pb2.WorkspaceGroupInfo())

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_user_svc = WorkspaceGroupUserService(metadata)
        response: dict = workspace_group_user_svc.list(params)
        return ParseDict(response, workspace_group_pb2.WorkspaceGroupsInfo())

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        workspace_group_user_svc = WorkspaceGroupUserService(metadata)
        response: dict = workspace_group_user_svc.stat(params)
        return self.dict_to_message(response)
