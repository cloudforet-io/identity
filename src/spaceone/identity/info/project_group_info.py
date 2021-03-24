import functools
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.identity.v1 import project_group_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.project_model import Project
from spaceone.identity.model.project_group_model import ProjectGroup
from spaceone.identity.info.role_info import RoleInfo

__all__ = ['ProjectGroupInfo', 'ProjectGroupsInfo', 'ProjectGroupRoleBindingInfo', 'ProjectGroupRoleBindingsInfo',
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
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in project_group_vo.tags],
            'domain_id': project_group_vo.domain_id,
            'created_by': project_group_vo.created_by,
            'created_at': change_timestamp_type(project_group_vo.created_at)
        })

        # Temporary code for DB migration
        if not project_group_vo.parent_project_group_id and project_group_vo.parent_project_group:
            project_group_vo.update({'parent_project_group_id': project_group_vo.parent_project_group.project_group_id})

    return project_group_pb2.ProjectGroupInfo(**info)


def ProjectGroupsInfo(project_group_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectGroupInfo, **kwargs), project_group_vos))
    return project_group_pb2.ProjectGroupsInfo(results=results, total_count=total_count)


def ProjectGroupRoleBindingInfo(role_binding_vo):
    info = {
        'role_binding_id': role_binding_vo.role_binding_id,
        'resource_type': role_binding_vo.resource_type,
        'resource_id': role_binding_vo.resource_id,
        'role_info': RoleInfo(role_binding_vo.role, minimal=True),
        'project_group_info': ProjectGroupInfo(role_binding_vo.project_group, minimal=True),
        'labels': role_binding_vo.labels,
        'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in role_binding_vo.tags],
        'domain_id': role_binding_vo.domain_id,
        'created_at': change_timestamp_type(role_binding_vo.created_at)
    }

    return project_group_pb2.ProjectGroupRoleBindingInfo(**info)


def ProjectGroupRoleBindingsInfo(role_binding_vos, total_count, **kwargs):
    results = list(map(ProjectGroupRoleBindingInfo, role_binding_vos))

    return project_group_pb2.ProjectGroupRoleBindingsInfo(results=results, total_count=total_count)


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
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in project_vo.tags],
            'domain_id': project_vo.domain_id,
            'created_by': project_vo.created_by,
            'created_at': change_timestamp_type(project_vo.created_at)
        })

    return project_group_pb2.ProjectGroupProjectInfo(**info)


def ProjectGroupProjectsInfo(project_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectGroupProjectInfo, **kwargs), project_vos))
    return project_group_pb2.ProjectGroupProjectsInfo(results=results, total_count=total_count)
