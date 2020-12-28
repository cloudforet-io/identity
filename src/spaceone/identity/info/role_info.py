import functools
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.identity.v1 import role_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.role_model import Role, RolePolicy

__all__ = ['RoleInfo', 'RolesInfo']


def RolePolicyInfo(role_policy_vo: RolePolicy):
    role_policy_info = {
        'policy_type': role_policy_vo.policy_type,
        'policy_id': role_policy_vo.policy.policy_id
    }

    return role_policy_info


def RoleInfo(role_vo: Role, minimal=False):
    info = {
        'role_id': role_vo.role_id,
        'name': role_vo.name,
        'role_type': role_vo.role_type
    }

    if not minimal:
        info.update({
            'policies': list(map(lambda policy: RolePolicyInfo(policy), role_vo.policies)),
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in role_vo.tags],
            'domain_id': role_vo.domain_id,
            'created_at': change_timestamp_type(role_vo.created_at)
        })

    return role_pb2.RoleInfo(**info)


def RolesInfo(role_vos, total_count, **kwargs):
    results = list(map(functools.partial(RoleInfo, **kwargs), role_vos))

    return role_pb2.RolesInfo(results=results, total_count=total_count)
