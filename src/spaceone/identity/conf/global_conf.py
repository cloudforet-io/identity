DATABASE_AUTO_CREATE_INDEX = True
DATABASE_CASE_INSENSITIVE_INDEX = False
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
        'refresh_ttl': 12,
        'refresh_once': True
    }
}

HANDLERS = {
    # 'authentication': [{
    #     'backend': 'spaceone.core.handler.authentication_handler.AuthenticationGRPCHandler',
    #     'uri': 'grpc://localhost:50051/v1/Domain/get_public_key'
    # }],
    # 'authorization': [{
    #     'backend': 'spaceone.core.handler.authorization_handler.AuthorizationGRPCHandler',
    #     'uri': 'grpc://localhost:50051/v1/Authorization/verify'
    # }],
    # 'mutation': [{
    #     'backend': 'spaceone.core.handler.mutation_handler.SpaceONEMutationHandler'
    # }],
    # 'event': []
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
    'RepositoryConnector': {
        'endpoint': {
            'v1': 'grpc://repository:50051'
        }
    },
}

ENDPOINTS = [
    # {
    #     'service': 'identity',
    #     'name': 'Identity Service',
    #     'endpoint': 'grpc://<endpoint>>:<port>/v1'
    # },
]
