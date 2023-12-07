from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Project(MongoModel):
    project_id = StringField(max_length=40, generate_id="project", unique=True)
    name = StringField(max_length=40)
    project_type = StringField(max_length=20, default="PRIVATE", choices=("PRIVATE", "PUBLIC"))
    tags = DictField(default=None)
    users = ListField(StringField(max_length=40), default=None)
    user_groups = ListField(StringField(max_length=255), default=None)
    project_group_id = StringField(max_length=40, default=None, null=True)
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": [
            "name",
            "project_type",
            "tags",
            "users",
            "user_groups",
            "project_group_id",
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
            "user_group_id": "user_groups",
        },
        "ordering": ["name"],
        "indexes": [
            "project_type",
            "users",
            "user_groups",
            "project_group_id",
            "workspace_id",
            "domain_id",
        ],
    }
