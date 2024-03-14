from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import project_group_pb2, project_group_pb2_grpc
from spaceone.identity.service.project_group_service import ProjectGroupService


class ProjectGroup(BaseAPI, project_group_pb2_grpc.ProjectGroupServicer):
    pb2 = project_group_pb2
    pb2_grpc = project_group_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.update(params)
        return self.dict_to_message(response)

    def change_parent_group(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.change_parent_group(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        project_group_svc.delete(params)
        return self.empty()

    def add_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.add_users(params)
        return self.dict_to_message(response)

    def remove_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.remove_users(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_group_svc = ProjectGroupService(metadata)
        response: dict = project_group_svc.stat(params)
        return self.dict_to_message(response)
