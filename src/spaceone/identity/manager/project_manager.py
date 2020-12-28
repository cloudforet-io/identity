import logging
from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.model.project_model import Project
from spaceone.identity.model.project_group_model import ProjectGroup

_LOGGER = logging.getLogger(__name__)


class ProjectManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_model: Project = self.locator.get_model('Project')
        self.project_group_model: ProjectGroup = self.locator.get_model('ProjectGroup')

    def create_project(self, params):
        def _rollback(project_vo):
            _LOGGER.info(f'[create_project._rollback] Delete project : {project_vo.name} ({project_vo.project_id})')
            project_vo.delete()

        project_vo: Project = self.project_model.create(params)
        self.transaction.add_rollback(_rollback, project_vo)

        return project_vo

    def update_project(self, params):
        project_vo = self.get_project(params['project_id'], params['domain_id'])
        return self.update_project_by_vo(params, project_vo)

    def update_project_by_vo(self, params, project_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_project._rollback] Revert Data : {old_data["name"]} ({old_data["project_id"]})')
            project_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_vo.to_dict())

        if 'project_group' in params:
            domain_id = project_vo.project_group.domain_id
            new_project_group_id = params['project_group'].project_group_id
            old_project_group_id = project_vo.project_group.project_group_id

            cache.delete_pattern(f'project-group-children:{domain_id}:{new_project_group_id}')
            cache.delete_pattern(f'project-group-children:{domain_id}:{old_project_group_id}')

        return project_vo.update(params)

    def delete_project(self, project_id, domain_id):
        project_vo = self.get_project(project_id, domain_id)
        self.delete_project_by_vo(project_vo)

    @staticmethod
    def delete_project_by_vo(project_vo):
        domain_id = project_vo.domain_id
        if project_vo.project_group:
            project_group_id = project_vo.project_group.project_group_id
        else:
            project_group_id = None

        project_vo.delete()

        if project_group_id:
            cache.delete_pattern(f'project-group-children:{domain_id}:{project_group_id}')

    def get_project(self, project_id, domain_id, only=None):
        return self.project_model.get(project_id=project_id, domain_id=domain_id, only=only)

    def list_projects(self, query):
        return self.project_model.query(**query)

    def stat_projects(self, query):
        return self.project_model.stat(**query)
