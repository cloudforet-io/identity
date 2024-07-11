from spaceone.core.pygrpc import BaseAPI
from spaceone.api.identity.v2 import project_pb2, project_pb2_grpc
from spaceone.identity.service.project_service import ProjectService


class Project(BaseAPI, project_pb2_grpc.ProjectServicer):
    pb2 = project_pb2
    pb2_grpc = project_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.create(params)
        return self.dict_to_message(response)

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.update(params)
        return self.dict_to_message(response)

    def update_project_type(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.update_project_type(params)
        return self.dict_to_message(response)

    def change_project_group(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.change_project_group(params)
        return self.dict_to_message(response)

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        project_svc.delete(params)
        return self.empty()

    def add_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.add_users(params)
        return self.dict_to_message(response)

    def remove_users(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.remove_users(params)
        return self.dict_to_message(response)

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.get(params)
        return self.dict_to_message(response)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.list(params)
        return self.dict_to_message(response)

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)
        project_svc = ProjectService(metadata)
        response: dict = project_svc.stat(params)
        return self.dict_to_message(response)
