from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class Policy(MongoModel):
    policy_id = StringField(max_length=40, generate_id='policy', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    permissions = ListField(StringField())
    tags = DictField()
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'permissions',
            'tags'
        ],
        'exact_fields': [
            'policy_id',
            'domain_id'
        ],
        'minimal_fields': [
            'policy_id',
            'name'
        ],
        'ordering': ['name'],
        'indexes': [
            'policy_id',
            'domain_id'
        ]
    }
