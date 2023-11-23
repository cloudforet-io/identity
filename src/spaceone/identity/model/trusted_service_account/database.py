from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class TrustedServiceAccount(MongoModel):
    trusted_service_account_id = StringField(max_length=40, generate_id='tsa', unique=True)
    name = StringField(max_length=255, unique_with=['workspace_id', 'domain_id'])
    data = DictField(default=None)
    provider = StringField(max_length=40)
    tags = DictField(default=None)
    scope = StringField(max_length=40, choices=('DOMAIN', 'WORKSPACE'), default='WORKSPACE')
    workspace_id = StringField(max_length=40, default='*')
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'data',
            'tags'
        ],
        'minimal_fields': [
            'trusted_service_account_id',
            'name',
            'provider'
        ],
        'change_query_keys': {
            'user_workspaces': 'workspace_id'
        },
        'ordering': ['name'],
        'indexes': [
            'name',
            'provider',
            'scope',
            'workspace_id',
            'domain_id'
        ]
    }
