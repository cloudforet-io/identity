from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class RoleBinding(MongoModel):
    role_binding_id = StringField(max_length=40, generate_id='rb', unique=True)
    role_type = StringField(
        max_length=20,
        choices=('SYSTEM_ADMIN', 'DOMAIN_ADMIN', 'WORKSPACE_OWNER', 'WORKSPACE_MEMBER')
    )
    user_id = StringField(max_length=255)
    role_id = StringField(max_length=40)
    scope = StringField(max_length=40, choices=('DOMAIN', 'WORKSPACE'), default='WORKSPACE')
    workspace_id = StringField(max_length=40, default='*')
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'role_id',
            'role_type',
        ],
        'minimal_fields': [
            'role_binding_id',
            'role_type',
            'user_id',
            'role_id',
            'workspace_id'
        ],
        'change_query_keys': {
            'user_workspaces': 'workspace_id'
        },
        'indexes': [
            'role_type',
            'user_id',
            'role_id',
            'scope',
            'workspace_id',
            'domain_id',
        ]
    }