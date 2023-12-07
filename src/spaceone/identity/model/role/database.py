from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class PagePermission(EmbeddedDocument):
    page = StringField(required=True)
    permission = StringField(max_length=20, choices=('VIEW', 'MANAGE'), required=True)


class Role(MongoModel):
    role_id = StringField(max_length=40, required=True, unique_with='domain_id')
    name = StringField(max_length=255, unique_with='domain_id')
    version = StringField(max_length=40, default=None, null=True)
    role_type = StringField(
        max_length=20,
        choices=('SYSTEM', 'SYSTEM_ADMIN', 'DOMAIN_ADMIN', 'WORKSPACE_OWNER', 'WORKSPACE_MEMBER')
    )
    api_permissions = ListField(StringField(max_length=255), default=[])
    page_permissions = ListField(EmbeddedDocumentField(PagePermission), default=[])
    tags = DictField(default=None)
    is_managed = BooleanField(default=False)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        'updatable_fields': [
            'name',
            'api_permissions',
            'page_permissions',
            'tags',
            'updated_at'
        ],
        'minimal_fields': [
            'role_id',
            'name',
            'role_type',
            'is_managed'
        ],
        'ordering': ['name'],
        'indexes': [
            'role_type',
            'domain_id'
        ]
    }