from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class ExternalAuth(MongoModel):
    domain_id = StringField(max_length=40, unique=True)
    state = StringField(
        max_length=20, default="ENABLED", choices=("ENABLED", "DISABLED")
    )
    plugin_info = DictField(default=None)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "state",
            "plugin_info",
            "updated_at",
        ]
    }
