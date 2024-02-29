from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Provider(MongoModel):
    provider = StringField(max_length=40, unique_with="domain_id")
    name = StringField(max_length=40)
    plugin_info = DictField(default=None, null=True)
    version = StringField(max_length=40, default=None, null=True)
    alias = StringField(max_length=40, default=None, null=True)
    color = StringField(max_length=7, default=None, null=True)
    icon = StringField(default=None, null=True)
    order = IntField(min_value=1, default=10)
    options = DictField(default=None)
    tags = DictField(default=None)
    is_managed = BooleanField(default=False)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "name",
            "plugin_info",
            "version",
            "alias",
            "color",
            "icon",
            "order",
            "options",
            "tags",
            "updated_at",
        ],
        "minimal_fields": ["provider", "name", "order", "is_managed"],
        "ordering": ["order", "name"],
        "indexes": ["provider", "is_managed", "domain_id"],
    }
