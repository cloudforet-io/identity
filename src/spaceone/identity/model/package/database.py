from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Package(MongoModel):
    package_id = StringField(max_length=40, generate_id="p", unique=True)
    name = StringField(max_length=255, unique_with=["domain_id"])
    description = StringField(max_length=255, default=None, null=True)
    order = IntField(required=True)
    is_default = BooleanField(default=False)
    tags = DictField(Default=None)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": ["name", "description", "order", "is_default", "tags"],
        "minimal_fields": [
            "package_id",
            "name",
            "is_default",
            "domain_id",
        ],
        "ordering": ["order"],
        "indexes": [
            "name",
            "domain_id",
        ],
    }
