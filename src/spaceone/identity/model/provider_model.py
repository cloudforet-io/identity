from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class ProviderTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class Provider(MongoModel):
    provider = StringField(max_length=40, unique=True)
    name = StringField(max_length=255)
    template = DictField()
    metadata = DictField()
    capability = DictField()
    tags = ListField(EmbeddedDocumentField(ProviderTag))
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'template',
            'metadata',
            'capability',
            'tags'
        ],
        'minimal_fields': [
            'provider',
            'name'
        ],
        'ordering': ['created_at'],
        'indexes': [
            'provider',
            ('tags.key', 'tags.value')
        ]
    }
