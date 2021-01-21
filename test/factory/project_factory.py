import factory

from spaceone.core import utils
from spaceone.identity.model.project_model import Project
from test.factory.project_group_factory import ProjectGroupFactory


class ProjectFactory(factory.mongoengine.MongoEngineFactory):

    class Meta:
        model = Project

    project_id = factory.LazyAttribute(lambda o: utils.generate_id('project'))
    name = factory.LazyAttribute(lambda o: utils.random_string())
    project_group = factory.SubFactory(ProjectGroupFactory)
    project_group_id = factory.LazyAttribute(lambda o: utils.generate_id('pg'))
    tags = [
        {
            'key': 'tag_key',
            'value': 'tag_value'
        }
    ]
    domain_id = utils.generate_id('domain')
    created_by = factory.Faker('name')
    created_at = factory.Faker('date_time')
