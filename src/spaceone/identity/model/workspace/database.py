from datetime import datetime

from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class Workspace(MongoModel):
    workspace_id = StringField(max_length=40, generate_id="workspace", unique=True)
    name = StringField(max_length=255)
    state = StringField(max_length=20, default="ENABLED")
    tags = DictField(default=None)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    deleted_at = DateTimeField(default=None, null=True)

    meta = {
        "updatable_fields": ["name", "state", "tags", "deleted_at"],
        "minimal_fields": [
            "workspace_id",
            "name",
            "state",
        ],
        "ordering": ["name"],
        "indexes": ["name", "domain_id"],
    }

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.filter(state__ne="DELETED")

    @classmethod
    def create(cls, data):
        workspace_vos = cls.filter(name=data["name"], domain_id=data["domain_id"])
        if workspace_vos.count() > 0:
            raise ERROR_NOT_UNIQUE(key="name", value=data["name"])

        return super().create(data)

    def delete(self):
        self.update({"state": "DELETED", "deleted_at": datetime.utcnow()})
