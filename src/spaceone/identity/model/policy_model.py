from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class PolicyTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class Policy(MongoModel):
    policy_id = StringField(max_length=40, generate_id='policy', unique_with='domain_id')
    name = StringField(max_length=255, unique_with=['domain_id', 'policy_type'])
    policy_type = StringField(max_length=20, default='CUSTOM', choices=('CUSTOM', 'MANAGED'))
    permissions = ListField(StringField())
    tags = ListField(EmbeddedDocumentField(PolicyTag))
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
        'exact_fields': [
            'policy_id',
            'policy_type',
            'domain_id'
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
            ('tags.key', 'tags.value')
        ]
    }
