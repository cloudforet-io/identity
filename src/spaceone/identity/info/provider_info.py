import functools
from spaceone.api.identity.v1 import provider_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.identity.model.provider_model import Provider

__all__ = ['ProviderInfo', 'ProvidersInfo']


def ProviderInfo(provider_vo: Provider, minimal=False):
    info = {
        'provider': provider_vo.provider,
        'name': provider_vo.name,
        'order': provider_vo.order
    }

    if not minimal:
        info.update({
            'template': change_struct_type(provider_vo.template),
            'metadata': change_struct_type(provider_vo.metadata),
            'capability': change_struct_type(provider_vo.capability),
            'tags': change_struct_type(provider_vo.tags),
            'domain_id': provider_vo.domain_id,
            'created_at': utils.datetime_to_iso8601(provider_vo.created_at)
        })

    return provider_pb2.ProviderInfo(**info)


def ProvidersInfo(provider_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProviderInfo, **kwargs), provider_vos))

    return provider_pb2.ProvidersInfo(results=results, total_count=total_count)
