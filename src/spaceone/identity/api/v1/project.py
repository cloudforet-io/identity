from spaceone.api.identity.v1 import project_pb2, project_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Project(BaseAPI, project_pb2_grpc.ProjectServicer):

    pb2 = project_pb2
    pb2_grpc = project_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            return self.locator.get_info('ProjectInfo', project_svc.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            return self.locator.get_info('ProjectInfo', project_svc.update(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            project_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            return self.locator.get_info('ProjectInfo', project_svc.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            project_vos, total_count = project_svc.list(params)
            return self.locator.get_info('ProjectsInfo', project_vos, total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            return self.locator.get_info('StatisticsInfo', project_svc.stat(params))

    def add_member(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            return self.locator.get_info('ProjectRoleBindingInfo', project_svc.add_member(params))

    def modify_member(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            return self.locator.get_info('ProjectRoleBindingInfo', project_svc.modify_member(params))

    def remove_member(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            project_svc.remove_member(params)
            return self.locator.get_info('EmptyInfo')

    def list_members(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectService', metadata) as project_svc:
            project_map_vos, total_count = project_svc.list_members(params)
            return self.locator.get_info('ProjectRoleBindingsInfo', project_map_vos, total_count,
                                         minimal=self.get_minimal(params))
