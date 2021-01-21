from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel


class ProjectGroupTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class ProjectGroup(MongoModel):
    project_group_id = StringField(max_length=40, generate_id='pg', unique=True)
    name = StringField(max_length=40)
    parent_project_group = ReferenceField('self', null=True, default=None, reverse_delete_rule=DENY)
    parent_project_group_id = StringField(max_length=40, null=True, default=None)
    tags = ListField(EmbeddedDocumentField(ProjectGroupTag))
    domain_id = StringField(max_length=255)
    created_by = StringField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'parent_project_group',
            'parent_project_group_id',
            'tags'
        ],
        'minimal_fields': [
            'project_group_id',
            'name'
        ],
        'reference_query_keys': {
            'parent_project_group': 'self'
        },
        'ordering': ['name'],
        'indexes': [
            'project_group_id',
            'parent_project_group',
            'domain_id',
            ('tags.key', 'tags.value')
        ]
    }
