from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class TrustedAccount(MongoModel):
    trusted_account_id = StringField(max_length=40, generate_id='ta', unique=True)
    name = StringField(max_length=255, unique_with=['domain_id'])
    data = DictField(default=None)
    provider = StringField(max_length=40)
    tags = DictField(default=None)
    permission_group = StringField(max_length=40, choices=('DOMAIN', 'WORKSPACE'))
    workspace_id = StringField(max_length=40)
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'data',
            'tags'
        ],
        'minimal_fields': [
            'trusted_account_id',
            'name',
            'provider',
            'permission_group',
            'workspace_id'
        ],
        'ordering': ['name'],
        'indexes': [
            'provider',
            'permission_group',
            'workspace_id',
            'domain_id'
        ]
    }
