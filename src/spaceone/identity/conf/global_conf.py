DATABASES = {
    'default': {
        # 'db': '',
        # 'host': '',
        # 'port': 0,
        # 'username': '',
        # 'password': '',
        # 'ssl': False,
        # 'ssl_ca_certs': ''
    }
}

CACHES = {
    'default': {},
    'local': {
        'backend': 'spaceone.core.cache.local_cache.LocalCache',
        'max_size': 128,
        'ttl': 86400
    }
}

IDENTITY = {
    'token': {
        'token_timeout': 1800,
        'refresh_timeout': 3600,
        'refresh_ttl': 6
    }
}

SYSTEM_METHODS = []

HANDLERS = {
    # TODO: add system key authentication handler
    'authentication': [{
        'backend': 'spaceone.core.handler.authentication_handler.AuthenticationGRPCHandler',
        'uri': 'grpc://localhost:50051/v1/Domain/get_public_key'
    }],
    'authorization': [{
        'backend': 'spaceone.core.handler.authorization_handler.AuthorizationGRPCHandler',
        'uri': 'grpc://localhost:50051/v1/Authorization/verify'
    }],
    'event': []
}

CONNECTORS = {
    'IdentityConnector': {
        'endpoint': {
            'v1': 'grpc://localhost:50051'
        }
    },
    'PluginServiceConnector': {
        'endpoint': {
            'v1': 'grpc://plugin:50051'
        }
    },
    'SecretConnector': {
        'endpoint': {
            'v1': 'grpc://secret:50051'
        }
    },
}

ENDPOINTS = {}

LOG = {}
