from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class App(MongoModel):
    app_id = StringField(max_length=40, generate_id="app", unique=True)
    name = StringField(max_length=40, required=True)
    state = StringField(
        max_length=20, default="ENABLED", choices=("ENABLED", "DISABLED", "EXPIRED")
    )
    role_type = StringField(
        max_length=20,
        default="WORKSPACE_MEMBER",
        choices=(
            "SYSTEM",
            "SYSTEM_ADMIN",
            "DOMAIN_ADMIN",
            "WORKSPACE_OWNER",
            "WORKSPACE_MEMBER",
        ),
    )
    api_key_id = StringField(max_length=40, default=None, null=True)
    role_id = StringField(max_length=40, required=True)

    domain_id = StringField(max_length=40, required=True)
    created_at = DateTimeField(auto_now_add=True)
    last_accessed_at = DateTimeField(default=None, null=True)
    expired_at = DateTimeField(required=True)

    meta = {
        "updatable_fields": ["name", "state", "api_key_id", "tags", "last_accessed_at"],
        "minimal_fields": ["app_id", "state", "expired_at", "api_key_id"],
        "ordering": ["app_id"],
        "indexes": ["state", "domain_id", "last_accessed_at", "expired_at"],
    }
