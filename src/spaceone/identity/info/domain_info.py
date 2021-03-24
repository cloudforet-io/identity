import functools
import json

from spaceone.api.core.v1 import handler_pb2
from spaceone.api.core.v1 import tag_pb2
from spaceone.api.identity.v1 import domain_pb2

from spaceone.core.pygrpc.message_type import *
from spaceone.identity.model.domain_model import Domain

__all__ = ['DomainInfo', 'DomainsInfo', 'DomainPublicKeyInfo']


def DomainInfo(domain_vo: Domain, minimal=False):
    info = {
        'domain_id': domain_vo.domain_id,
        'name': domain_vo.name,
        'state': domain_vo.state
    }

    if not minimal:
        info.update({
            'plugin_info': PluginInfo(domain_vo.plugin_info),
            'config': change_struct_type(domain_vo.config),
            'created_at': change_timestamp_type(domain_vo.created_at),
            'deleted_at': change_timestamp_type(domain_vo.deleted_at),
            'tags': [tag_pb2.Tag(key=tag.key, value=tag.value) for tag in domain_vo.tags]
        })

    return domain_pb2.DomainInfo(**info)


def DomainsInfo(domain_vos, total_count, **kwargs):
    results = list(map(functools.partial(DomainInfo, **kwargs), domain_vos))

    return domain_pb2.DomainsInfo(results=results, total_count=total_count)


def PluginInfo(plugin_info):
    if plugin_info:
        info = {
            'plugin_id': plugin_info.plugin_id,
            'version': plugin_info.version,
            'options': change_struct_type(plugin_info.options),
            'secret_id': plugin_info.secret_id
        }
        return domain_pb2.PluginInfo(**info)
    return None


def DomainPublicKeyInfo(public_key, domain_id):
    info = {
        'public_key': json.dumps(public_key).__str__(),
        'domain_id': domain_id
    }
    return handler_pb2.AuthenticationResponse(**info)
