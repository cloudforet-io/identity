from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Project(MongoModel):
    project_id = StringField(max_length=40, generate_id="project", unique=True)
    name = StringField(max_length=40)
    project_type = StringField(max_length=20, default="PRIVATE")
    tags = DictField(default=None)
    users = ListField(StringField(max_length=255), default=None)
    user_groups = ListField(StringField(max_length=255), default=None)
    project_group_id = StringField(max_length=40, default=None)
    workspace_id = StringField(max_length=255)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": [
            "name",
            "tags",
            "project_type",
            "project_group_id",
            "users",
            "user_groups",
        ],
        "minimal_fields": ["project_id", "name", "project_type"],
        # "change_query_keys": {
        #     "user_groups": "project_id",
        #     "project_group_id": "project_group.project_group_id",
        # },
        "ordering": ["name"],
        "indexes": [
            # 'project_id',
            "project_type",
            "workspace_id",
            "domain_id",
        ],
    }
