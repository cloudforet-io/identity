from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Project(MongoModel):
    project_id = StringField(max_length=40, generate_id="project", unique=True)
    name = StringField(max_length=255)
    project_type = StringField(
        max_length=20, default="PRIVATE", choices=("PRIVATE", "PUBLIC")
    )
    tags = DictField(default=None)
    users = ListField(StringField(max_length=40), default=None)
    created_by = StringField(max_length=255)
    reference_id = StringField(max_length=255, default=None, null=True)
    is_managed = BooleanField(default=False)
    trusted_account_id = StringField(max_length=40, default=None, null=True)
    project_group_id = StringField(max_length=40, default=None, null=True)
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    last_synced_at = DateTimeField(default=None, null=True)

    meta = {
        "updatable_fields": [
            "name",
            "project_type",
            "tags",
            "users",
            "is_managed",
            "trusted_account_id",
            "project_group_id",
            "last_synced_at",
        ],
        "minimal_fields": [
            "project_id",
            "name",
            "project_type",
            "project_group_id",
            "workspace_id",
        ],
        "change_query_keys": {
            "user_projects": "project_id",
            "user_id": "users",
        },
        "ordering": ["name"],
        "indexes": [
            "project_type",
            "users",
            "project_group_id",
            "workspace_id",
            "domain_id",
        ],
    }
