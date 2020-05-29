import functools
from spaceone.api.identity.v1 import project_group_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.project_model import Project
from spaceone.identity.model.project_group_model import ProjectGroup
from spaceone.identity.info.user_info import UserInfo
from spaceone.identity.info.role_info import RoleInfo

__all__ = ['ProjectGroupInfo', 'ProjectGroupsInfo', 'ProjectGroupMemberInfo', 'ProjectGroupMembersInfo',
           'ProjectGroupProjectsInfo']


def ProjectGroupInfo(project_group_vo: ProjectGroup, minimal=False):
    info = {
        'project_group_id': project_group_vo.project_group_id,
        'name': project_group_vo.name
    }

    if not minimal:
        if project_group_vo.parent_project_group:
            info.update({
                'parent_project_group_info': ProjectGroupInfo(project_group_vo.parent_project_group, minimal=True)
            })

        info.update({
            'tags': change_struct_type(project_group_vo.tags),
            'domain_id': project_group_vo.domain_id,
            'created_by': project_group_vo.created_by,
            'created_at': change_timestamp_type(project_group_vo.created_at)
        })

        # info.update({
        #       'template_id': ''   TODO: Template service is NOT be implemented yet
        #       'fields': [],       TODO: Template service is NOT be implemented yet
        # })

    return project_group_pb2.ProjectGroupInfo(**info)


def ProjectGroupsInfo(project_group_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectGroupInfo, **kwargs), project_group_vos))
    return project_group_pb2.ProjectGroupsInfo(results=results, total_count=total_count)


def ProjectGroupMemberInfo(project_group_member_vo):
    info = {
        'project_group_info': ProjectGroupInfo(project_group_member_vo.project_group, minimal=True),
        'user_info': UserInfo(project_group_member_vo.user),
        'roles': list(map(lambda role: RoleInfo(role, minimal=True), project_group_member_vo.roles)),
        'labels': change_list_value_type(project_group_member_vo.labels)
    }

    return project_group_pb2.ProjectGroupMemberInfo(**info)


def ProjectGroupMembersInfo(project_group_map_vos, total_count, **kwargs):
    results = list(map(ProjectGroupMemberInfo, project_group_map_vos))

    return project_group_pb2.ProjectGroupMembersInfo(results=results, total_count=total_count)


def ProjectGroupProjectInfo(project_vo: Project, minimal=False):
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

    return project_group_pb2.ProjectGroupProjectInfo(**info)


def ProjectGroupProjectsInfo(project_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectGroupProjectInfo, **kwargs), project_vos))
    return project_group_pb2.ProjectGroupProjectsInfo(results=results, total_count=total_count)
