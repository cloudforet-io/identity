from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel

class RolePolicy(EmbeddedDocument):
    policy_type = StringField(max_length=20, choices=('MANAGED', 'CUSTOM'))
    url = StringField(default=None, null=True)
    policy = ReferenceField('Policy', default=None, null=True)

class Role(MongoModel):
    role_id = StringField(max_length=40, generate_id='role', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    role_type = StringField(max_length=20)
    tags = DictField()
    policies = ListField(EmbeddedDocumentField(RolePolicy))
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'policies',
            'tags'
        ],
        'exact_fields': [
            'role_id',
            'role_type'
        ],
        'minimal_fields': [
            'role_id',
            'name',
            'role_type'
        ],
        'ordering': ['name'],
        'indexes': [
            'role_id',
            'role_type',
            'domain_id'
        ]
    }
