from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel

class Provider(MongoModel):
    provider = StringField(max_length=40, unique=True)
    name = StringField(max_length=255)
    template = DictField()
    metadata = DictField()
    capability = DictField()
    tags = DictField()
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'template',
            'metadata',
            'capability',
            'tags'
        ],
        'exact_fields': [
            'provider'
        ],
        'minimal_fields': [
            'provider',
            'name'
        ],
        'ordering': ['name'],
        'indexes': [
            'provider'
        ]
    }
