from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class RolePolicy(EmbeddedDocument):
    policy_type = StringField(max_length=20, choices=('MANAGED', 'CUSTOM'))
    policy = ReferenceField('Policy')


class RoleTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class Role(MongoModel):
    role_id = StringField(max_length=40, generate_id='role', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    role_type = StringField(max_length=20, choices=('SYSTEM', 'DOMAIN', 'PROJECT'))
    tags = ListField(EmbeddedDocumentField(RoleTag))
    policies = ListField(EmbeddedDocumentField(RolePolicy))
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'policies',
            'tags'
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
            'domain_id',
            ('tags.key', 'tags.value')
        ]
    }
