from spaceone.api.identity.v1 import project_group_pb2, project_group_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class ProjectGroup(BaseAPI, project_group_pb2_grpc.ProjectGroupServicer):

    pb2 = project_group_pb2
    pb2_grpc = project_group_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            return self.locator.get_info('ProjectGroupInfo', project_group_svc.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            return self.locator.get_info('ProjectGroupInfo', project_group_svc.update(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            project_group_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def add_member(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            return self.locator.get_info('ProjectGroupMemberInfo', project_group_svc.add_member(params))

    def modify_member(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            return self.locator.get_info('ProjectGroupMemberInfo', project_group_svc.modify_member(params))

    def remove_member(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            project_group_svc.remove_member(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            return self.locator.get_info('ProjectGroupInfo', project_group_svc.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            project_group_vos, total_count = project_group_svc.list(params)
            return self.locator.get_info('ProjectGroupsInfo', project_group_vos, total_count,
                                         minimal=self.get_minimal(params))

    def list_projects(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            project_vos, total_count = project_group_svc.list_projects(params)
            return self.locator.get_info('ProjectGroupProjectsInfo', project_vos, total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            return self.locator.get_info('StatisticsInfo', project_group_svc.stat(params))

    def list_members(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectGroupService', metadata) as project_group_svc:
            project_group_map_vos, total_count = project_group_svc.list_members(params)
            return self.locator.get_info('ProjectGroupMembersInfo', project_group_map_vos, total_count,
                                         minimal=self.get_minimal(params))
