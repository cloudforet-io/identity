import factory

from spaceone.core import utils
from spaceone.identity.model.project_group_model import ProjectGroup


class ProjectGroupFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = ProjectGroup

    project_group_id = factory.LazyAttribute(lambda o: utils.generate_id('pg'))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    parent_project_group = None
    parent_project_group_id = None
    tags = [
        {
            'key': 'tag_key',
            'value': 'tag_value'
        }
    ]
    domain_id = utils.generate_id('domain')
    created_by = factory.Faker('name')
    created_at = factory.Faker('date_time')
