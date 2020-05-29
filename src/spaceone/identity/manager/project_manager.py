import logging
from spaceone.core.manager import BaseManager
from spaceone.identity.model.project_model import Project, ProjectMemberMap
from spaceone.identity.model.project_group_model import ProjectGroup

_LOGGER = logging.getLogger(__name__)


class ProjectManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_model: Project = self.locator.get_model('Project')
        self.project_group_model: ProjectGroup = self.locator.get_model('ProjectGroup')
        self.project_map_model: ProjectMemberMap = self.locator.get_model('ProjectMemberMap')

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

        return project_vo.update(params)

    def delete_project(self, project_id, domain_id):
        project_vo = self.get_project(project_id, domain_id)
        self.delete_project_by_vo(project_vo)

    @staticmethod
    def delete_project_by_vo(project_vo):
        project_vo.delete()

    def get_project(self, project_id, domain_id, only=None):
        return self.project_model.get(project_id=project_id, domain_id=domain_id, only=only)

    def list_projects(self, query):
        return self.project_model.query(**query)

    def stat_projects(self, query):
        return self.project_model.stat(**query)

    @staticmethod
    def add_member(project_vo, user_vo, roles, labels):
        return project_vo.append('members', {
            'user': user_vo,
            'roles': roles,
            'labels': labels
        })

    @staticmethod
    def remove_member(project_vo, project_member_vo):
        project_vo.remove('members', project_member_vo)

    def list_project_members(self, query):
        return self.project_map_model.query(**query)
