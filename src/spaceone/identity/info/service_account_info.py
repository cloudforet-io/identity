import functools
from spaceone.api.identity.v1 import service_account_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.service_account_model import ServiceAccount
from spaceone.identity.info.project_info import ProjectInfo

__all__ = ['ServiceAccountInfo', 'ServiceAccountsInfo']


def ServiceAccountInfo(service_account_vo: ServiceAccount, minimal=False):
    info = {
        'service_account_id': service_account_vo.service_account_id,
        'name': service_account_vo.name,
        'provider': service_account_vo.provider
    }

    if not minimal:
        info.update({
            'data': change_struct_type(service_account_vo.data),
            'tags': change_struct_type(service_account_vo.tags),
            'domain_id': service_account_vo.domain_id,
            'created_at': change_timestamp_type(service_account_vo.created_at)
        })

        if service_account_vo.project:
            info.update({
                'project_info': ProjectInfo(service_account_vo.project, minimal=True)
            })

    return service_account_pb2.ServiceAccountInfo(**info)


def ServiceAccountsInfo(service_account_vos, total_count, **kwargs):
    results = list(map(functools.partial(ServiceAccountInfo, **kwargs), service_account_vos))

    return service_account_pb2.ServiceAccountsInfo(results=results, total_count=total_count)
