from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Role(MongoModel):
    role_id = StringField(max_length=40, required=True, unique_with="domain_id")
    name = StringField(max_length=255, unique_with="domain_id")
    state = StringField(choices=("ENABLED", "DISABLED"), default="ENABLED")
    version = StringField(max_length=40, default=None, null=True)
    role_type = StringField(
        max_length=20,
        choices=(
            "DOMAIN_ADMIN",
            "WORKSPACE_OWNER",
            "WORKSPACE_MEMBER",
        ),
    )
    permissions = ListField(StringField(max_length=255), default=[])
    page_access = ListField(StringField(max_length=255), default=[])
    tags = DictField(default=None)
    is_managed = BooleanField(default=False)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "name",
            "state",
            "permissions",
            "page_access",
            "tags",
            "updated_at",
        ],
        "minimal_fields": ["role_id", "name", "role_type", "is_managed", "state"],
        "ordering": ["name"],
        "indexes": ["role_type", "domain_id"],
    }
