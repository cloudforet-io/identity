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
        'ttl': 300
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
    'SpaceConnector': {
        'backend': 'spaceone.core.connector.space_connector.SpaceConnector',
        'endpoints': {
            'plugin': 'grpc://plugin:50051',
            'secret': 'grpc://secret:50051',
            'repository': 'grpc://repository:50051'
        }
    }
}

ENDPOINTS = [
    # {
    #     'service': 'identity',
    #     'name': 'Identity Service',
    #     'endpoint': 'grpc://<endpoint>>:<port>/v1'
    # },
]

# Internal Endpoint
INTERNAL_ENDPOINTS = [
    {
        'service': 'identity',
        'name': 'Identity Service',
        'endpoint': 'grpc://identity.spaceone.svc.cluster.local:50051/v1'
    },
    {
        'service': 'secret',
        'name': 'Secret Service',
        'endpoint': 'grpc://secret.spaceone.svc.cluster.local:50051/v1'
    },
    {
        'service': 'repository',
        'name': 'Repository Service',
        'endpoint': 'grpc://repository.spaceone.svc.cluster.local:50051/v1'
    },
    {
        'service': 'plugin',
        'name': 'Plugin Service',
        'endpoint': 'grpc://plugin.spaceone.svc.cluster.local:50051/v1'
    },
    {
        'service': 'config',
        'name': 'Config Service',
        'endpoint': 'grpc://config.spaceone.svc.cluster.local:50051/v1'
    },
    {
        'service': 'inventory',
        'name': 'Inventory Service',
        'endpoint': 'grpc://inventory.spaceone.svc.cluster.local:50051/v1'
    },
    {
        'service': 'monitoring',
        'name': 'Monitoring Service',
        'endpoint': 'grpc://monitoring.spaceone.svc.cluster.local:50051/v1'
    },
    {
        'service': 'statistics',
        'name': 'Statistics Service',
        'endpoint': 'grpc://statistics.spaceone.svc.cluster.local:50051/v1'
    }
]
