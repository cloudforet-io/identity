from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class UserGroup(MongoModel):
    user_group_id = StringField(max_length=40, generate_id="ug", unique=True)
    name = StringField(max_length=255, unique_with=["domain_id", "workspace_id"])
    users = ListField(StringField(max_length=40), default=[])
    tags = DictField(Default=None)
    workspace_id = StringField(max_length=40, required=True)
    domain_id = StringField(max_length=40)

    meta = {
        "updatable_fields": ["name", "users", "tags"],
        "minimal_fields": [
            "user_group_id",
            "name",
            "users",
            "workspace_id",
            "domain_id",
        ],
        "ordering": ["name", "user_group_id"],
        "indexes": [
            "name",
            "workspace_id",
        ],
    }
