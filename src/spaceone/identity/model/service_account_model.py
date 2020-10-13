from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.project_model import Project

class ServiceAccount(MongoModel):
    service_account_id = StringField(max_length=40, generate_id='sa', unique=True)
    name = StringField(max_length=255, unique_with='domain_id')
    data = DictField()
    provider = StringField(max_length=40)
    project = ReferenceField('Project', null=True, default=None, reverse_delete_rule=DENY)
    tags = DictField()
    domain_id = StringField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'data',
            'project',
            'tags'
        ],
        'exact_fields': [
            'service_account_id',
            'provider',
            'project',
            'domain_id'
        ],
        'minimal_fields': [
            'service_account_id',
            'name',
            'domain_id'
        ],
        'change_query_keys': {
            'project_id': 'project.project_id'
        },
        'reference_query_keys': {
            'project': Project
        },
        'ordering': ['name'],
        'indexes': [
            'service_account_id',
            'provider',
            'project',
            'domain_id'
        ],
        'aggregate': {
            'lookup': {
                'project': {
                    'from': 'project'
                }
            }
        }
    }
