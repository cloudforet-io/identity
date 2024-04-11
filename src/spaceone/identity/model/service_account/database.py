from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class ServiceAccount(MongoModel):
    service_account_id = StringField(max_length=40, generate_id="sa", unique=True)
    name = StringField(
        max_length=255, unique_with=["domain_id", "workspace_id", "project_id"]
    )
    data = DictField(default=None)
    provider = StringField(max_length=40)
    tags = DictField(default=None)
    reference_id = StringField(max_length=255, default=None, null=True)
    is_managed = BooleanField(default=False)
    secret_schema_id = StringField(max_length=40)
    secret_id = StringField(max_length=40)
    trusted_account_id = StringField(max_length=40, null=True, default=None)
    project_id = StringField(max_length=40)
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    last_synced_at = DateTimeField(default=None, null=True)

    meta = {
        "updatable_fields": [
            "name",
            "data",
            "tags",
            "is_managed",
            "secret_schema_id",
            "secret_id",
            "trusted_account_id",
            "project_id",
            "last_synced_at",
        ],
        "minimal_fields": [
            "service_account_id",
            "name",
            "provider",
            "is_managed",
            "trusted_account_id",
            "project_id",
            "workspace_id",
        ],
        "change_query_keys": {"user_projects": "project_id"},
        "ordering": ["name"],
        "indexes": [
            "name",
            "provider",
            "secret_schema_id",
            "secret_id",
            "trusted_account_id",
            "project_id",
            "workspace_id",
            "domain_id",
        ],
    }
