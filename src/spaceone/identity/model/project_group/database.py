from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class ProjectGroup(MongoModel):
    project_group_id = StringField(max_length=40, generate_id="pg", unique=True)
    name = StringField(max_length=255)
    tags = DictField(default=None)
    users = ListField(StringField(max_length=255), default=None)
    reference_id = StringField(max_length=255, default=None, null=True)
    is_managed = BooleanField(default=False)
    trusted_account_id = StringField(max_length=40, default=None, null=True)
    parent_group_id = StringField(max_length=40, null=True, default=None)
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    last_synced_at = DateTimeField(default=None, null=True)

    meta = {
        "updatable_fields": [
            "name",
            "tags",
            "users",
            "is_managed",
            "trusted_account_id",
            "parent_group_id",
            "last_synced_at",
        ],
        "minimal_fields": [
            "project_group_id",
            "name",
            "parent_group_id",
            "workspace_id",
        ],
        "change_query_keys": {
            "user_id": "users",
        },
        "ordering": ["name"],
        "indexes": [
            "parent_group_id",
            "workspace_id",
            "domain_id",
        ],
    }
