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

        if params.get('parent_project_group') is not None:
            parent_project_group_id = params['parent_project_group_id']
            cache.delete_pattern(f'project-path:*{parent_project_group_id}*')
            cache.delete_pattern(f'role-bindings:*{parent_project_group_id}*')
            cache.delete_pattern(f'user-scopes:*{parent_project_group_id}*')
            self._delete_parent_project_group_cache(params['parent_project_group'])

        return project_group_vo

    def update_project_group(self, params):
        project_group_vo = self.get_project_group(params['project_group_id'], params['domain_id'])
        return self.update_project_group_by_vo(params, project_group_vo)

    def update_project_group_by_vo(self, params, project_group_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_project_group._rollback] Revert Data : {old_data["name"]} ({old_data["project_group_id"]})')
            project_group_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_group_vo.to_dict())

        if params.get('parent_project_group') is not None:
            parent_project_group_id = params['parent_project_group_id']
            project_group_id = project_group_vo.project_group_id

            if parent_project_group_id is not None:
                cache.delete_pattern(f'project-path:*{parent_project_group_id}*')
                cache.delete_pattern(f'role-bindings:*{parent_project_group_id}*')
                cache.delete_pattern(f'user-scopes:*{parent_project_group_id}*')
                self._delete_parent_project_group_cache(params['parent_project_group'])

            cache.delete_pattern(f'project-path:*{project_group_id}*')
            cache.delete_pattern(f'role-bindings:*{project_group_id}*')
            cache.delete_pattern(f'user-scopes:*{project_group_id}*')
            self._delete_parent_project_group_cache(project_group_vo)

        return project_group_vo.update(params)

    def delete_project_group(self, project_group_id, domain_id):
        project_group_vo = self.get_project_group(project_group_id, domain_id)
        self.delete_project_group_by_vo(project_group_vo)

    def delete_project_group_by_vo(self, project_group_vo):
        project_group_vo.delete()

        cache.delete_pattern(f'project-path:*{project_group_vo.project_group_id}*')
        cache.delete_pattern(f'role-bindings:*{project_group_vo.project_group_id}*')
        cache.delete_pattern(f'role-bindings:*:')
        cache.delete_pattern(f'user-scopes:*{project_group_vo.project_group_id}*')
        self._delete_parent_project_group_cache(project_group_vo)

    def get_project_group(self, project_group_id, domain_id, only=None):
        return self.project_group_model.get(project_group_id=project_group_id, domain_id=domain_id, only=only)

    def filter_project_groups(self, **conditions):
        return self.project_group_model.filter(**conditions)

    def list_project_groups(self, query):
        return self.project_group_model.query(**query)

    def stat_project_groups(self, query):
        return self.project_group_model.stat(**query)

    def _delete_parent_project_group_cache(self, project_group_vo):
        cache.delete_pattern(f'project-group-children:*{project_group_vo.project_group_id}')
        if project_group_vo.parent_project_group:
            self._delete_parent_project_group_cache(project_group_vo.parent_project_group)
