from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.project_group_model import ProjectGroup


class ProjectTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class Project(MongoModel):
    project_id = StringField(max_length=40, generate_id='project', unique=True)
    name = StringField(max_length=40)
    project_group = ReferenceField('ProjectGroup', reverse_delete_rule=DENY)
    project_group_id = StringField(max_length=40)
    tags = ListField(EmbeddedDocumentField(ProjectTag))
    domain_id = StringField(max_length=255)
    created_by = StringField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'project_group',
            'project_group_id',
            'tags'
        ],
        'minimal_fields': [
            'project_id',
            'name'
        ],
        'change_query_keys': {
            'user_projects': 'project_id',
            'project_group_id': 'project_group.project_group_id'
        },
        'reference_query_keys': {
            'project_group': ProjectGroup
        },
        'ordering': ['name'],
        'indexes': [
            'project_id',
            'project_group',
            'project_group_id',
            'domain_id',
            ('tags.key', 'tags.value')
        ]
    }
