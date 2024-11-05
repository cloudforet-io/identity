from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Schema(MongoModel):
    schema_id = StringField(max_length=40, unique_with="domain_id")
    name = StringField(max_length=40)
    version = StringField(max_length=40, default=None, null=True)
    schema_type = StringField(
        max_length=20,
        choices=("SERVICE_ACCOUNT", "TRUSTED_ACCOUNT", "SECRET", "TRUSTING_SECRET"),
    )
    schema = DictField(default=None)
    provider = StringField(max_length=40)
    related_schemas = ListField(StringField(max_length=40), default=None)
    options = DictField(default=None)
    tags = DictField(default=None)
    is_managed = BooleanField(default=False)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "name",
            "version",
            "schema",
            "related_schemas",
            "options",
            "tags",
            "updated_at",
        ],
        "minimal_fields": [
            "schema_id",
            "name",
            "schema_type",
            "provider",
            "is_managed",
            "version",
        ],
        "change_query_keys": {
            "related_schema_id": "related_schemas",
        },
        "ordering": ["name"],
        "indexes": [
            "schema_id",
            "schema_type",
            "provider",
            "related_schemas",
            "is_managed",
            "domain_id",
        ],
    }
