import logging
from spaceone.core.manager import BaseManager
from spaceone.identity.model.project_group_model import ProjectGroup, ProjectGroupMemberMap

_LOGGER = logging.getLogger(__name__)


class ProjectGroupManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_group_model: ProjectGroup = self.locator.get_model('ProjectGroup')
        self.project_group_map_model: ProjectGroupMemberMap = self.locator.get_model('ProjectGroupMemberMap')

    def create_project_group(self, params):
        def _rollback(project_group_vo):
            _LOGGER.info(
                f'[create_project_group._rollback] Delete project group : {project_group_vo.name} ({project_group_vo.project_group_id})')
            project_group_vo.delete()

        project_group_vo: ProjectGroup = self.project_group_model.create(params)
        self.transaction.add_rollback(_rollback, project_group_vo)

        return project_group_vo

    def update_project_group(self, params):
        project_group_vo = self.get_project_group(params['project_group_id'], params['domain_id'])
        return self.update_project_group_by_vo(params, project_group_vo)

    def update_project_group_by_vo(self, params, project_group_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_project_group._rollback] Revert Data : {old_data["name"]} ({old_data["project_group_id"]})')
            project_group_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_group_vo.to_dict())

        return project_group_vo.update(params)

    def delete_project_group(self, project_group_id, domain_id):
        project_group_vo = self.get_project_group(project_group_id, domain_id)
        self.delete_project_group_by_vo(project_group_vo)

    def get_project_group(self, project_group_id, domain_id, only=None):
        return self.project_group_model.get(project_group_id=project_group_id, domain_id=domain_id, only=only)

    def list_project_groups(self, query):
        return self.project_group_model.query(**query)

    def stat_project_groups(self, query):
        return self.project_group_model.stat(**query)

    @staticmethod
    def delete_project_group_by_vo(project_group_vo):
        project_group_vo.delete()

    @staticmethod
    def add_member(project_group_vo, user_vo, roles, labels):
        return project_group_vo.append('members', {
            'user': user_vo,
            'roles': roles,
            'labels': labels
        })

    @staticmethod
    def remove_member(project_group_vo, project_group_member_vo):
        project_group_vo.remove('members', project_group_member_vo)

    def list_project_group_members(self, query):
        return self.project_group_map_model.query(**query)
