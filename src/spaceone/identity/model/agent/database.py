from mongoengine import StringField, DictField, DateTimeField
from spaceone.core.model.mongo_model import MongoModel


class Agent(MongoModel):
    agent_id = StringField(max_length=40, generate_id="agent", unique=True)
    options = DictField(default=None)
    app_id = StringField(max_length=40)
    service_account_id = StringField(max_length=40)
    project_id = StringField(max_length=40)
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        "minimal_fields": [
            "agent_id",
            "options",
            "service_account_id",
        ],
        "change_query_keys": {"user_projects": "project_id"},
        "ordering": ["-created_at"],
        "indexes": [
            "service_account_id",
            "workspace_id",
            "domain_id",
        ],
    }
