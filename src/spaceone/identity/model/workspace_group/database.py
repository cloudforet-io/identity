from mongoengine import (
    DateTimeField,
    DictField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
    ListField,
    StringField,
)
from spaceone.core.model.mongo_model import MongoModel


class WorkspaceGroupUser(EmbeddedDocument):
    user_id = StringField(max_length=40, required=True)
    role_id = StringField(max_length=40, required=True)
    role_type = StringField(
        max_length=20, choices=("WORKSPACE_OWNER", "WORKSPACE_MEMBER")
    )


class WorkspaceGroup(MongoModel):
    workspace_group_id = StringField(max_length=40, generate_id="wg", unique=True)
    name = StringField(max_length=255, unique_with="domain_id")
    workspace_count = IntField(default=None)
    users = ListField(
        EmbeddedDocumentField(WorkspaceGroupUser), default=None, null=True
    )
    tags = DictField(default=None)
    created_by = StringField(max_length=255)
    updated_by = StringField(max_length=255)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "name",
            "workspace_count",
            "users",
            "tags",
            "updated_by",
            "updated_at",
        ],
        "minimal_fields": [
            "workspace_group_id",
            "name",
        ],
        "change_query_keys": {},
        "ordering": ["name"],
        "indexes": [
            "name",
        ],
    }
