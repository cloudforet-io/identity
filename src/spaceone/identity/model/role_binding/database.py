from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class RoleBinding(MongoModel):
    role_binding_id = StringField(max_length=40, generate_id="rb", unique=True)
    role_type = StringField(
        max_length=20,
        choices=("DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"),
    )
    user_id = StringField(max_length=255)
    role_id = StringField(max_length=40)
    resource_group = StringField(max_length=40, choices=("DOMAIN", "WORKSPACE"))
    workspace_id = StringField(max_length=40)
    workspace_group_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": [
            "role_id",
            "role_type",
        ],
        "minimal_fields": [
            "role_binding_id",
            "role_type",
            "user_id",
            "role_id",
            "workspace_id",
        ],
        "indexes": [
            {
                "fields": [
                    "role_type",
                    "user_id",
                    "role_id",
                    "resource_group",
                    "workspace_id",
                    "domain_id",
                ],
                "name": "COMPOUND_INDEX_FOR_SEARCH_1",
            },
            {
                "fields": [
                    "workspace_id",
                    "domain_id",
                ],
                "name": "COMPOUND_INDEX_FOR_ROLE_BINDING_UPDATE",
            },
        ],
    }
