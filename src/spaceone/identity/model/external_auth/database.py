from mongoengine import *
from datetime import datetime
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class ExternalAuth(MongoModel):
    domain_id = StringField(max_length=40, unique=True)
    state = StringField(max_length=20, default="ENABLED")
    plugin_info = DictField(default={})
    updated_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": [
            "name",
            "state",
            "plugin_info",
            "updated_at",
        ],
        "minimal_fields": ["domain_id", "state", "updated_at"],
        "ordering": ["name"],
        "indexes": [
            # 'domain_id',
            "state",
            "domain_id",
        ],
    }
