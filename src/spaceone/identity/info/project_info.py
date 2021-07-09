import functools
from spaceone.api.identity.v1 import project_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
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
            'tags': change_struct_type(utils.tags_to_dict(project_vo.tags)),
            'domain_id': project_vo.domain_id,
            'created_by': project_vo.created_by,
            'created_at': utils.datetime_to_iso8601(project_vo.created_at)
        })

    return project_pb2.ProjectInfo(**info)


def ProjectsInfo(project_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectInfo, **kwargs), project_vos))
    return project_pb2.ProjectsInfo(results=results, total_count=total_count)


def ProjectRoleBindingInfo(role_binding_vo, minimal=False):
    info = {
        'role_binding_id': role_binding_vo.role_binding_id,
        'resource_type': role_binding_vo.resource_type,
        'resource_id': role_binding_vo.resource_id,
        'role_info': RoleInfo(role_binding_vo.role, minimal=True) if role_binding_vo.role else None
    }

    if not minimal:
        info.update({
            'project_info': ProjectInfo(role_binding_vo.project, minimal=True) if role_binding_vo.project else None,
            'project_group_info': ProjectGroupInfo(role_binding_vo.project_group, minimal=True) if role_binding_vo.project_group else None,
            'labels': change_list_value_type(role_binding_vo.labels),
            'tags': change_struct_type(utils.tags_to_dict(role_binding_vo.tags)),
            'domain_id': role_binding_vo.domain_id,
            'created_at': utils.datetime_to_iso8601(role_binding_vo.created_at)
        })

    return project_pb2.ProjectRoleBindingInfo(**info)


def ProjectRoleBindingsInfo(role_binding_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProjectRoleBindingInfo, **kwargs), role_binding_vos))

    return project_pb2.ProjectRoleBindingsInfo(results=results, total_count=total_count)
