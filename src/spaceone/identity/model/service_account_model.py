from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.project_model import Project


class ServiceAccount(MongoModel):
    service_account_id = StringField(max_length=40, generate_id='sa', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    data = DictField()
    service_account_type = StringField(max_length=40, choices=('TRUSTED', 'GENERAL'), default='GENERAL')
    provider = StringField(max_length=40)
    project = ReferenceField('Project', null=True, default=None, reverse_delete_rule=DENY)
    project_id = StringField(max_length=40, default=None, null=True)
    trusted_service_account_id = StringField(max_length=40, null=True, default=None)
    tags = DictField()
    scope = StringField(max_length=40, choices=('DOMAIN', 'PROJECT'), default='PROJECT')
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'data',
            'project',
            'project_id',
            'trusted_service_account_id',
            'tags'
        ],
        'minimal_fields': [
            'service_account_id',
            'service_account_type',
            'name',
            'provider'
        ],
        'change_query_keys': {
            'user_projects': 'project_id',
            'project_id': 'project_id'
        },
        'reference_query_keys': {
            'project': Project
        },
        'ordering': ['name'],
        'indexes': [
            # 'service_account_id',
            'name',
            'provider',
            'project',
            'project_id',
            'trusted_service_account_id',
            'scope',
            'domain_id'
        ]
    }
