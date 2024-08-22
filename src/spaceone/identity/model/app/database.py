from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class App(MongoModel):
    app_id = StringField(max_length=40, generate_id="app", unique=True)
    name = StringField(max_length=40, required=True)
    state = StringField(
        max_length=20, default="ENABLED", choices=("ENABLED", "DISABLED", "EXPIRED")
    )
    is_managed = BooleanField(default=False)
    tags = DictField(default=None)
    role_type = StringField(
        max_length=20,
        choices=("DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"),
    )

    client_id = StringField(max_length=40, default=None, null=True)
    role_id = StringField(max_length=40, required=True)
    resource_group = StringField(
        max_length=40, choices=("DOMAIN", "WORKSPACE", "PROJECT")
    )
    project_id = StringField(max_length=40, default=None, null=True)
    project_group_id = StringField(max_length=40, default=None, null=True)
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    expired_at = DateTimeField(required=True)
    last_accessed_at = DateTimeField(default=None, null=True)

    meta = {
        "updatable_fields": [
            "name",
            "state",
            "client_id",
            "tags",
            "expired_at",
            "last_accessed_at",
        ],
        "minimal_fields": [
            "app_id",
            "name",
            "state",
            "role_type",
            "role_id",
            "expired_at",
        ],
        "ordering": ["-created_at"],
        "indexes": [
            "state",
            "role_type",
            "client_id",
            "role_id",
            "resource_group",
            "workspace_id",
            "domain_id",
        ],
    }
