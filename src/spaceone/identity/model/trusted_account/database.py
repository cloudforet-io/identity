from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class TrustedAccount(MongoModel):
    trusted_account_id = StringField(max_length=40, generate_id="ta", unique=True)
    name = StringField(max_length=255, unique_with=["domain_id"])
    data = DictField(default=None)
    provider = StringField(max_length=40)
    schedule = DictField(default=None, null=True)
    sync_options = DictField(default=None, null=True)
    plugin_options = DictField(default=None, null=True)
    tags = DictField(default=None)
    secret_schema_id = StringField(max_length=40)
    trusted_secret_id = StringField(max_length=40)
    resource_group = StringField(max_length=40, choices=("DOMAIN", "WORKSPACE"))
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": [
            "name",
            "data",
            "schedule",
            "sync_options",
            "plugin_options",
            "tags",
            "secret_schema_id",
            "trusted_secret_id",
        ],
        "minimal_fields": [
            "trusted_account_id",
            "name",
            "provider",
            "sync_options",
            "secret_schema_id",
            "trusted_secret_id",
            "resource_group",
            "workspace_id",
        ],
        "ordering": ["name"],
        "indexes": [
            "provider",
            "secret_schema_id",
            "trusted_secret_id",
            "resource_group",
            "workspace_id",
            "domain_id",
        ],
    }
