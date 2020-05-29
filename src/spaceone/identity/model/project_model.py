from datetime import datetime
from mongoengine import *
from spaceone.core.model.mongo_model import MongoModel
from spaceone.identity.model.user_model import User
from spaceone.identity.model.project_group_model import ProjectGroup


class Project(MongoModel):
    project_id = StringField(max_length=40, generate_id='project', unique=True)
    name = StringField(max_length=40)
    state = StringField(max_length=20, default='ACTIVE')
    project_group = ReferenceField('ProjectGroup', reverse_delete_rule=DENY)
    tags = DictField()
    domain_id = StringField(max_length=255)
    created_by = StringField(max_length=255, null=True)
    created_at = DateTimeField(auto_now_add=True)
    deleted_at = DateTimeField(default=None, null=True)

    meta = {
        'updatable_fields': [
            'name',
            'state',
            'project_group',
            # TODO: Template service is NOT be implemented yet
            # 'template',
            'tags',
            'deleted_at'
        ],
        'exact_fields': [
            'project_id',
            'state',
            'domain_id'
        ],
        'minimal_fields': [
            'project_id',
            'name',
            'state',
        ],
        'change_query_keys': {
            'project_group_id': 'project_group.project_group_id'
        },
        'reference_query_keys': {
            'project_group': ProjectGroup
        },
        'ordering': ['name'],
        'indexes': [
            'project_id',
            'state',
            'project_group',
            'domain_id'
        ],
        'aggregate': {
            'lookup': {
                'project_group': {
                    'from': 'project_group',
                    # 'localField': 'project_group',
                    # 'foreignField': '_id'
                },
                'project_member': {
                    'from': 'project_member_map',
                    'localField': '_id',
                    'foreignField': 'project'
                },
                'project_member.user': {
                    'from': 'user',
                    # 'localField': 'project_member.user',
                    # 'foreignField': '_id'
                }
            }
        }
    }

    def append(self, key, data):
        if key == 'members':
            data.update({
                'project': self
            })

            project_member_vo = ProjectMemberMap.create(data)
            return project_member_vo
        else:
            super().append(key, data)
            return self

    def remove(self, key, data):
        if key == 'members':
            data.delete()
        else:
            super().remove(key, data)


class ProjectMemberMap(MongoModel):
    project = ReferenceField('Project', reverse_delete_rule=CASCADE)
    user = ReferenceField('User', reverse_delete_rule=CASCADE)
    roles = ListField(ReferenceField('Role', reverse_delete_rule=DENY))
    labels = ListField(StringField(max_length=255))

    meta = {
        'reference_query_keys': {
            'project': Project,
            'user': User
        },
        'change_query_keys': {
            'project_id': 'project.project_id',
            'project_name': 'project.name',
            'user_id': 'user.user_id',
            'user_name': 'user.name',
            'email': 'user.email',
            'mobile': 'user.mobile',
            'language': 'user.language',
            'timezone': 'user.timezone'
        },
        'indexes': [
            'project',
            'user'
        ]
    }
