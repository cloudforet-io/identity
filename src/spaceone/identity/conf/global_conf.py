# Email Settings
EMAIL_CONSOLE_DOMAIN = ""
EMAIL_SERVICE_NAME = "Cloudforet"
MFA_OTP_ISSUER_NAME = "Cloudforet"

# Enums: ACCESS_TOKEN (default) | PASSWORD
RESET_PASSWORD_TYPE = "ACCESS_TOKEN"

# WORKSPACE COLORS
WORKSPACE_COLORS_NAME = [
    "blue",
    "yellow",
    "gray",
    "green",
    "coral",
    "indigo",
    "peacock",
]

# Dormancy Settings
DORMANCY_CHECK_HOUR = 14
DORMANCY_SETTINGS_KEY = "identity:dormancy:workspace"

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
        "verify_code_timeout": 3600,  # 1hour
        "temporary_token_timeout": 86400,  # 24 hours
        "invite_token_timeout": 604800,  # 7 days
        "token_timeout": 1800,  # 30 minutes
        "token_max_timeout": 604800,  # 7 days
        "refresh_timeout": 10800,  # 3 hours
        "admin_refresh_max_timeout": 2419200,  # 28 days
    },
    "mfa": {"verify_code_timeout": 300},
    "max_issue_attempts": 10,
    "issue_block_time": 300,
}

# Handler Settings
HANDLERS = {
    # "authentication": [{
    #     "backend": "spaceone.core.handler.authentication_handler:SpaceONEAuthenticationHandler"
    # }],
    # "authorization": [{
    #     "backend": "spaceone.core.handler.authorization_handler:SpaceONEAuthorizationHandler"
    # }],
    # "mutation": [{
    #     "backend": "spaceone.core.handler.mutation_handler:SpaceONEMutationHandler"
    # }],
    # "event": []
}

# Log Settings
LOG = {
    "filters": {
        "masking": {
            "rules": {
                "Domain.create": ["admin"],
                "UserProfile.update": ["password"],
                "User.create": ["password"],
                "User.update": ["password"],
                "WorkspaceUser.create": ["password"],
                "Token.issue": ["credentials"],
                "Token.grant": ["token"],
                "Job.sync_service_accounts": ["secret_data"],
                "ServiceAccount.create": ["secret_data"],
                "ServiceAccount.update_secret_data": ["secret_data"],
            }
        }
    }
}

# Connector Settings
CONNECTORS = {
    "SpaceConnector": {
        "backend": "spaceone.core.connector.space_connector:SpaceConnector",
        "endpoints": {
            "identity": "grpc://localhost:50051",
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

# Queue Settings
QUEUES = {
    # "identity_q": {
    #     "backend": "spaceone.core.queue.redis_queue.RedisQueue",
    #     "host": "redis",
    #     "port": 6379,
    #     "channel": "identity_job",
    # },
}
SCHEDULERS = {}
WORKERS = {}

# System Token Settings
TOKEN = ""

# IDENTITY BASE URL for TOKEN PAYLOAD
IDENTITY_BASE_URL = ""

# Expiring App Check Days Settings
EXPIRING_APP_CHECK_HOUR = 0
EXPIRING_APP_CHECK_DAYS = []
