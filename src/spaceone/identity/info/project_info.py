import functools
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.identity.v1 import project_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.project_model import Project
from spaceone.identity.info.project_group_info import ProjectGroupInfo
from spaceone.identity.info.role_info import RoleInfo

__all__ = ['ProjectInfo', 'ProjectsInfo', 'ProjectRoleBindingInfo', 'ProjectRoleBindingsInfo']


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
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in project_vo.tags],
            'domain_id': project_vo.domain_id,
            'created_by': project_vo.created_by,
            'created_at': change_timestamp_type(project_vo.created_at)
        })

        # Temporary code for DB migration
        if not project_vo.project_group_id and project_vo.project_group:
            project_vo.update({'project_group_id': project_vo.project_group.project_group_id})

    return project_pb2.ProjectInfo(**info)


def ProjectsInfo(project_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectInfo, **kwargs), project_vos))
    return project_pb2.ProjectsInfo(results=results, total_count=total_count)


def ProjectRoleBindingInfo(role_binding_vo):
    info = {
        'role_binding_id': role_binding_vo.role_binding_id,
        'resource_type': role_binding_vo.resource_type,
        'resource_id': role_binding_vo.resource_id,
        'role_info': RoleInfo(role_binding_vo.role, minimal=True),
        'project_info': ProjectInfo(role_binding_vo.project, minimal=True),
        'labels': role_binding_vo.labels,
        'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in role_binding_vo.tags],
        'domain_id': role_binding_vo.domain_id,
        'created_at': change_timestamp_type(role_binding_vo.created_at)
    }

    return project_pb2.ProjectRoleBindingInfo(**info)


def ProjectRoleBindingsInfo(role_binding_vos, total_count, **kwargs):
    results = list(map(ProjectRoleBindingInfo, role_binding_vos))

    return project_pb2.ProjectRoleBindingsInfo(results=results, total_count=total_count)
