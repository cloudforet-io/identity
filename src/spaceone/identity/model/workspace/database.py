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

    meta = {
        "updatable_fields": ["name", "state", "tags"],
        "minimal_fields": [
            "workspace_id",
            "name",
            "state",
        ],
        "ordering": ["name"],
        "indexes": [
            "state",
        ],
    }

    @classmethod
    def create(cls, data):
        workspace_vos = cls.filter(name=data["name"])
        if workspace_vos.count() > 0:
            raise ERROR_NOT_UNIQUE(key="name", value=data["name"])

        return super().create(data)

    def update(self, data):
        if "name" in data:
            workspace_vos = self.filter(
                name=data["name"], workspace_id__ne=self.workspace_id
            )
            if workspace_vos.count() > 0:
                raise ERROR_NOT_UNIQUE(key="name", value=data["name"])

        return super().update(data)
