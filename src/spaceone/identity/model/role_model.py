from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel


class RolePolicy(EmbeddedDocument):
    policy_type = StringField(max_length=20, choices=('MANAGED', 'CUSTOM'))
    policy = ReferenceField('Policy')
    policy_id = StringField(max_length=40)

    def to_dict(self):
        return dict(self.to_mongo())


class PagePermission(EmbeddedDocument):
    page = StringField(max_length=255, required=True)
    permission = StringField(max_length=20, choices=('VIEW', 'MANAGE'))

    def to_dict(self):
        return dict(self.to_mongo())


class Role(MongoModel):
    role_id = StringField(max_length=40, generate_id='role', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    role_type = StringField(max_length=20, choices=('SYSTEM', 'DOMAIN', 'PROJECT'))
    tags = DictField(default={})
    policies = ListField(EmbeddedDocumentField(RolePolicy))
    page_permissions = ListField(EmbeddedDocumentField(PagePermission), default=[])
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'policies',
            'page_permissions',
            'tags'
        ],
        'minimal_fields': [
            'role_id',
            'name',
            'role_type',
            'page_permissions'
        ],
        'change_query_keys': {
            'policy_id': 'policies.policy_id'
        },
        'ordering': ['name'],
        'indexes': [
            # 'role_id',
            'role_type',
            'domain_id',
            'tags'
        ]
    }
