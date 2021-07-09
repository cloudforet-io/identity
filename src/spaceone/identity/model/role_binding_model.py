from mongoengine import *
from spaceone.core.error import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.role_model import Role
from spaceone.identity.model.project_model import Project
from spaceone.identity.model.project_group_model import ProjectGroup
from spaceone.identity.model.user_model import User


class RoleBindingTag(EmbeddedDocument):
    key = StringField(max_length=255)
    value = StringField(max_length=255)


class RoleBinding(MongoModel):
    role_binding_id = StringField(max_length=40, generate_id='rb', unique=True)
    resource_type = StringField(max_length=255)
    resource_id = StringField(max_length=255)
    role = ReferenceField('Role', reverse_delete_rule=DENY)
    project = ReferenceField('Project', null=True, default=None, reverse_delete_rule=CASCADE)
    project_group = ReferenceField('ProjectGroup', null=True, default=None, reverse_delete_rule=CASCADE)
    user = ReferenceField('User', null=True, default=None, reverse_delete_rule=CASCADE)
    role_id = StringField(max_length=40)
    project_id = StringField(max_length=40, null=True, default=None)
    project_group_id = StringField(max_length=40, null=True, default=None)
    labels = ListField(StringField(max_length=255))
    tags = ListField(EmbeddedDocumentField(RoleBindingTag))
    domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'labels',
            'tags',
            'role_id',
            'project_id',
            'project_group_id'
        ],
        'minimal_fields': [
            'role_binding_id',
            'resource_type',
            'resource_id',
            'role'
        ],
        'change_query_keys': {
            'user_id': 'user.user_id',
            'name': 'user.name',
            'email': 'user.email',
            'role_type': 'role.role_type',
            'project_group_id': 'project_group.project_group_id'
        },
        'reference_query_keys': {
            'user': User,
            'role': Role,
            'project': Project,
            'project_group': ProjectGroup
        },
        'ordering': ['resource_type', 'resource_id'],
        'indexes': [
            'role_binding_id',
            'resource_type',
            'resource_id',
            'role',
            'project',
            'project_group',
            'role_id',
            'project_id',
            'project_group_id',
            'domain_id',
            ('tags.key', 'tags.value')
        ]
    }
