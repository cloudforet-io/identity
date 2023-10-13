from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Provider(MongoModel):
    provider = StringField(max_length=40, unique_with='domain_id')
    name = StringField(max_length=255)
    order = IntField(min_value=1, default=10)
    template = DictField()
    metadata = DictField()
    capability = DictField()
    tags = DictField()
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'order',
            'template',
            'metadata',
            'capability',
            'tags'
        ],
        'minimal_fields': [
            'provider',
            'name',
            'order'
        ],
        'ordering': ['order', 'name']
    }
