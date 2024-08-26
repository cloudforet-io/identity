from mongoengine import DateTimeField, DictField, ListField, StringField
from spaceone.core.model.mongo_model import MongoModel


class WorkspaceGroup(MongoModel):
    workspace_group_id = StringField(max_length=40, generate_id="wg", unique=True)
    name = StringField(max_length=255, unique_with="domain_id")
    workspaces = ListField(StringField(max_length=40), default=None, null=True)
    users = ListField(DictField(default=None), default=None, null=True)
    tags = DictField(default=None)
    created_by = StringField(max_length=255)
    updated_by = StringField(max_length=255)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "name",
            "workspaces",
            "users",
            "tags",
            "updated_by",
            "updated_at",
        ],
        "minimal_fields": [
            "workspace_group_id",
            "name",
        ],
        "change_query_keys": {
            "workspace_id": "workspaces",
        },
        "ordering": ["name"],
        "indexes": [
            "workspace_group_id",
        ],
    }
