from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class ServiceAccount(MongoModel):
    service_account_id = StringField(max_length=40, generate_id='sa', unique=True)
    name = StringField(max_length=255, unique_with=['domain_id', 'workspace_id'])
    data = DictField(default=None)
    provider = StringField(max_length=40)
    tags = DictField(default=None)
    trusted_service_account_id = StringField(max_length=40, null=True, default=None)
    project_id = StringField(max_length=40)
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'data',
            'tags',
            'trusted_service_account_id',
            'project_id'
        ],
        'minimal_fields': [
            'service_account_id',
            'name',
            'provider'
            'trusted_service_account_id',
            'project_id'
        ],
        'change_query_keys': {
            'user_projects': 'project_id',
            'user_workspaces': 'workspace_id'
        },
        'ordering': ['name'],
        'indexes': [
            'name',
            'provider',
            'trusted_service_account_id',
            'project_id',
            'workspace_id',
            'domain_id'
        ]
    }
