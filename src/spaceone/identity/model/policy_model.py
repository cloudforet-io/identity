from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class Policy(MongoModel):
    policy_id = StringField(max_length=40, generate_id='policy', unique_with=['policy_type', 'domain_id'])
    name = StringField(max_length=255)
    policy_type = StringField(max_length=20, default='CUSTOM', choices=('CUSTOM', 'MANAGED'))
    permissions = ListField(StringField())
    tags = DictField()
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(default=None, null=True)

    meta = {
        'updatable_fields': [
            'name',
            'permissions',
            'tags',
            'updated_at'
        ],
        'minimal_fields': [
            'policy_id',
            'name'
        ],
        'ordering': ['name'],
        'indexes': [
            'policy_id',
            'policy_type',
            'domain_id',
        ]
    }
