import logging
from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.model.project_group_model import ProjectGroup

_LOGGER = logging.getLogger(__name__)


class ProjectGroupManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_group_model: ProjectGroup = self.locator.get_model('ProjectGroup')

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

        if 'parent_project_group' in params:
            domain_id = project_group_vo.domain_id
            new_parent_project_group_id = params['parent_project_group'].project_group_id
            if project_group_vo.parent_project_group:
                old_parent_project_group_id = project_group_vo.parent_project_group.project_group_id
            else:
                old_parent_project_group_id = None

            cache.delete_pattern(f'project-group-children:{domain_id}:{new_parent_project_group_id}')

            if old_parent_project_group_id:
                cache.delete_pattern(f'project-group-children:{domain_id}:{old_parent_project_group_id}')

        return project_group_vo.update(params)

    def delete_project_group(self, project_group_id, domain_id):
        project_group_vo = self.get_project_group(project_group_id, domain_id)
        self.delete_project_group_by_vo(project_group_vo)

    @staticmethod
    def delete_project_group_by_vo(project_group_vo):
        domain_id = project_group_vo.domain_id
        if project_group_vo.parent_project_group:
            parent_project_group_id = project_group_vo.parent_project_group.project_group_id
        else:
            parent_project_group_id = None

        project_group_vo.delete()

        if parent_project_group_id:
            cache.delete_pattern(f'project-group-children:{domain_id}:{parent_project_group_id}')

    def get_project_group(self, project_group_id, domain_id, only=None):
        return self.project_group_model.get(project_group_id=project_group_id, domain_id=domain_id, only=only)

    def list_project_groups(self, query):
        return self.project_group_model.query(**query)

    def stat_project_groups(self, query):
        return self.project_group_model.stat(**query)
