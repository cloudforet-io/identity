import functools
from spaceone.api.identity.v1 import policy_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.identity.model.policy_model import Policy

__all__ = ['PolicyInfo', 'PoliciesInfo']


def PolicyInfo(policy_vo: Policy, minimal=False):
    info = {
        'policy_id': policy_vo.policy_id,
        'name': policy_vo.name
    }

    if not minimal:
        info.update({
            'permissions': change_list_value_type(policy_vo.permissions),
            'tags': change_struct_type(utils.tags_to_dict(policy_vo.tags)),
            'domain_id': policy_vo.domain_id,
            'created_at': utils.datetime_to_iso8601(policy_vo.created_at)
        })

    return policy_pb2.PolicyInfo(**info)


def PoliciesInfo(policy_vos, total_count, **kwargs):
    results = list(map(functools.partial(PolicyInfo, **kwargs), policy_vos))

    return policy_pb2.PoliciesInfo(results=results, total_count=total_count)
