import functools
from spaceone.api.identity.v1 import project_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.project_model import Project
from spaceone.identity.info.project_group_info import ProjectGroupInfo
from spaceone.identity.info.user_info import UserInfo
from spaceone.identity.info.role_info import RoleInfo

__all__ = ['ProjectInfo', 'ProjectsInfo', 'ProjectMemberInfo', 'ProjectMembersInfo']


def ProjectInfo(project_vo: Project, minimal=False):
    info = {
        'project_id': project_vo.project_id,
        'name': project_vo.name

    }

    if not minimal:
        if project_vo.project_group:
            info.update({
                'project_group_info': ProjectGroupInfo(project_vo.project_group, minimal=True)
            })

        info.update({
            'state': project_vo.state,
            'tags': change_struct_type(project_vo.tags),
            'domain_id': project_vo.domain_id,
            'created_by': project_vo.created_by,
            'created_at': change_timestamp_type(project_vo.created_at),
            'deleted_at': change_timestamp_type(project_vo.deleted_at)
        })

        # info.update({
        #       'template_data': '',        TODO: Template service is NOT be implemented yet
        #  })

    return project_pb2.ProjectInfo(**info)


def ProjectsInfo(project_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectInfo, **kwargs), project_vos))
    return project_pb2.ProjectsInfo(results=results, total_count=total_count)


def ProjectMemberInfo(project_member_vo):
    info = {
        'project_info': ProjectInfo(project_member_vo.project, minimal=True),
        'user_info': UserInfo(project_member_vo.user),
        'roles': list(map(lambda role: RoleInfo(role, minimal=True), project_member_vo.roles)),
        'labels': change_list_value_type(project_member_vo.labels)
    }

    return project_pb2.ProjectMemberInfo(**info)


def ProjectMembersInfo(project_group_map_vos, total_count, **kwargs):
    results = list(map(ProjectMemberInfo, project_group_map_vos))

    return project_pb2.ProjectMembersInfo(results=results, total_count=total_count)
