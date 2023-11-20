# Root Domain Settings
ROOT_DOMAIN_NAME = "root"

# Email Settings
EMAIL_CONSOLE_DOMAIN = ""
EMAIL_SERVICE_NAME = "Cloudforet"

# Enums: ACCESS_TOKEN (default) | PASSWORD
RESET_PASSWORD_TYPE = "ACCESS_TOKEN"

# Database Settings
DATABASE_AUTO_CREATE_INDEX = True
DATABASES = {
    "default": {
        # 'db': '',
        # 'host': '',
        # 'port': 0,
        # 'username': '',
        # 'password': '',
        # 'ssl': False,
        # 'ssl_ca_certs': ''
    }
}

# Cache Settings
CACHES = {
    "default": {},
    "local": {
        "backend": "spaceone.core.cache.local_cache.LocalCache",
        "max_size": 128,
        "ttl": 300,
    },
}

# Identity Settings
IDENTITY = {
    "token": {
        "verify_code_timeout": 3600,
        "temporary_token_timeout": 86400,  # 24 hours
        "token_timeout": 1200,
        "refresh_timeout": 1800,
        "refresh_ttl": 18,
        "refresh_once": False,
    },
    "mfa": {"mfa_verify_code_timeout": 300},
}

# Handler Settings
HANDLERS = {
    # "authentication": [{
    #     "backend": "spaceone.core.handler.authentication_handler.AuthenticationGRPCHandler",
    #     "uri": "grpc://localhost:50051/v1/Domain/get_public_key"
    # }],
    # "authorization": [{
    #     "backend": "spaceone.core.handler.authorization_handler.AuthorizationGRPCHandler",
    #     "uri": "grpc://localhost:50051/v1/Authorization/verify"
    # }],
    # "mutation": [{
    #     "backend": "spaceone.core.handler.mutation_handler.SpaceONEMutationHandler"
    # }],
    # "event": []
}

# Connector Settings
CONNECTORS = {
    "SpaceConnector": {
        "backend": "spaceone.core.connector.space_connector.SpaceConnector",
        "endpoints": {
            "plugin": "grpc://plugin:50051",
            "secret": "grpc://secret:50051",
            "repository": "grpc://repository:50051",
        },
    },
    "SMTPConnector": {
        # "host": "smtp.mail.com",
        # "port": "1234",
        # "user": "cloudforet",
        # "password": "1234",
        # "from_email": "support@cloudforet.com",
    },
}

# Endpoint Settings
ENDPOINTS = [
    # {
    #     "service": "identity",
    #     "name": "Identity Service",
    #     "endpoint": "grpc://<endpoint>>:<port>"
    # },
    # {
    #     "service": "inventory",
    #     "name": "Inventory Service",
    #     "endpoint": "grpc+ssl://<endpoint>>:<port>"
    # }
]
