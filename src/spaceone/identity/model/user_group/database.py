from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class UserGroup(MongoModel):
    user_group_id = StringField(max_length=40, generate_id="ug", unique=True)
    name = StringField(max_length=255, unique_with=["domain_id", "workspace_id"])
    description = StringField(max_length=255, default=None, null=True)
    users = ListField(StringField(max_length=40), default=[])
    tags = DictField(Default=None)
    workspace_id = StringField(max_length=40, required=True)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": ["name", "description", "users", "tags"],
        "minimal_fields": [
            "user_group_id",
            "name",
            "workspace_id",
            "domain_id",
        ],
        "change_query_keys": {"user_id": "users"},
        "ordering": ["name"],
        "indexes": [
            "name",
            "workspace_id",
            "domain_id",
            "users",
        ],
    }
