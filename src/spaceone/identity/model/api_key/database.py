from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class APIKey(MongoModel):
    api_key_id = StringField(max_length=40, generate_id="api-key", unique=True)
    name = StringField(max_length=40, default=None, null=True)
    state = StringField(
        max_length=20, default="ENABLED", choices=("ENABLED", "DISABLED", "EXPIRED")
    )
    user = ReferenceField("User", null=True, default=None, reverse_delete_rule=CASCADE)
    # app = ReferenceField("App", null=True, default=None, reverse_delete_rule=CASCADE)
    user_id = StringField(max_length=40, required=True)
    domain_id = StringField(max_length=40, required=True)
    last_accessed_at = DateTimeField(default=None, null=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "updatable_fields": ["state", "nane", "last_accessed_at"],
        "minimal_fields": ["api_key_id", "state", "user_id"],
        "ordering": ["api_key_id"],
        "indexes": ["state", "user_id", "domain_id", "last_accessed_at"],
    }
