from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class PagePermission(EmbeddedDocument):
    pages = ListField(StringField())
    permission = StringField(max_length=20, choices=('VIEW', 'MANAGE'))


class Role(MongoModel):
    role_id = StringField(max_length=40, generate_id='role', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    role_type = StringField(
        max_length=20,
        choices=('SYSTEM_ADMIN', 'DOMAIN_ADMIN', 'WORKSPACE_OWNER', 'WORKSPACE_MEMBER')
    )
    policies = ListField(StringField())
    policies_hash = StringField()
    page_permissions = ListField(EmbeddedDocumentField(PagePermission), default=[])
    page_permissions_hash = StringField()
    tags = DictField(default=None)
    is_managed = BooleanField(default=False)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'policies',
            'policies_hash',
            'page_permissions',
            'page_permissions_hash',
            'tags',
            'updated_at'
        ],
        'minimal_fields': [
            'role_id',
            'name',
            'role_type'
        ],
        'change_query_keys': {
            'policy_id': 'policies'
        },
        'ordering': ['name'],
        'indexes': [
            'role_type',
            'policies_hash',
            'page_permissions_hash',
            'domain_id'
        ]
    }