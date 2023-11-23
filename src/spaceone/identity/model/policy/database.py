from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class Policy(MongoModel):
    policy_id = StringField(max_length=40, generate_id='policy', unique_with='domain_id')
    name = StringField(max_length=255, unique_with='domain_id')
    permissions = ListField(StringField())
    permissions_hash = StringField()
    tags = DictField(default=None)
    is_managed = BooleanField(default=False)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(default=None, null=True)

    meta = {
        'updatable_fields': [
            'name',
            'permissions',
            'permissions_hash',
            'tags',
            'updated_at'
        ],
        'minimal_fields': [
            'policy_id',
            'name'
        ],
        'ordering': ['name'],
        'indexes': [
            'permissions_hash',
            'domain_id',
        ]
    }
