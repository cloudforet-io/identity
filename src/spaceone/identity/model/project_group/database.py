from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class ProjectGroup(MongoModel):
    project_group_id = StringField(max_length=40, generate_id="pg", unique=True)
    name = StringField(max_length=40)
    parent_project_group_id = StringField(max_length=40, null=True, default=None)
    tags = DictField(default=None)
    domain_id = StringField(max_length=255)
    workspace_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": [
            "name",
            "parent_project_group_id",
            "tags",
        ],
        "minimal_fields": ["project_group_id", "name", "workspace_id"],
        # "change_query_keys": {"user_project_groups": "project_group_id"},
        "ordering": ["name"],
        "indexes": [
            # 'project_group_id',
            "workspace_id",
            "domain_id",
        ],
    }
