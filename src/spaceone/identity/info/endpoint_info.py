import functools
from spaceone.api.identity.v1 import endpoint_pb2

__all__ = ['EndpointInfo', 'EndpointsInfo']


def EndpointInfo(endpoint_vo: dict, minimal=False):
    info = {
        'service': endpoint_vo['service'],
        'name': endpoint_vo['name'],
        'endpoint': endpoint_vo['endpoint'],
    }

    if not minimal:
        info.update({
            'state': endpoint_vo.get('state'),
            'version': endpoint_vo.get('version'),
        })

    return endpoint_pb2.EndpointInfo(**info)


def EndpointsInfo(endpoint_vos, total_count, **kwargs):
    results = list(map(functools.partial(EndpointInfo, **kwargs), endpoint_vos))

    return endpoint_pb2.EndpointsInfo(results=results, total_count=total_count)
