import functools
from spaceone.api.identity.v1 import role_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.identity.model.role_model import Role, RolePolicy, PagePermission

__all__ = ['RoleInfo', 'RolesInfo']


def RolePolicyInfo(role_policy_vo: RolePolicy):
    role_policy_info = {
        'policy_type': role_policy_vo.policy_type,
        'policy_id': role_policy_vo.policy_id
    }

    return role_policy_info


def PagePermissionInfo(page_perm_vo: PagePermission):
    page_perm_info = {
        'page': page_perm_vo.page,
        'permission': page_perm_vo.permission
    }

    return page_perm_info


def RoleInfo(role_vo: Role, minimal=False):
    # Temporary Code for Migration
    policies = []
    is_changed = False
    for policy_vo in role_vo.policies:
        if not policy_vo.policy_id:
            policy_vo.policy_id = policy_vo.policy.policy_id
            is_changed = True

        policies.append({
            'policy_type': policy_vo.policy_type,
            'policy': policy_vo.policy,
            'policy_id': policy_vo.policy_id
        })

    if is_changed:
        role_vo = role_vo.update({'policies': policies})

    info = {
        'role_id': role_vo.role_id,
        'name': role_vo.name,
        'role_type': role_vo.role_type,
        'page_permissions': list(map(lambda page_perm_vo: PagePermissionInfo(page_perm_vo), role_vo.page_permissions))
    }

    if not minimal:
        info.update({
            'policies': list(map(lambda policy: RolePolicyInfo(policy), role_vo.policies)),
            'tags': change_struct_type(role_vo.tags),
            'domain_id': role_vo.domain_id,
            'created_at': utils.datetime_to_iso8601(role_vo.created_at)
        })

    return role_pb2.RoleInfo(**info)


def RolesInfo(role_vos, total_count, **kwargs):
    results = list(map(functools.partial(RoleInfo, **kwargs), role_vos))

    return role_pb2.RolesInfo(results=results, total_count=total_count)
