import logging
from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.identity.manager import ProjectGroupManager
from spaceone.identity.model.project_model import Project

_LOGGER = logging.getLogger(__name__)


class ProjectManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_model: Project = self.locator.get_model('Project')
        self.project_group_mgr: ProjectGroupManager = self.locator.get_manager('ProjectGroupManager')

    def create_project(self, params):
        def _rollback(project_vo):
            _LOGGER.info(f'[create_project._rollback] Delete project : {project_vo.name} ({project_vo.project_id})')
            project_vo.delete()

        project_vo: Project = self.project_model.create(params)
        self.transaction.add_rollback(_rollback, project_vo)

        project_group_id = params['project_group_id']
        cache.delete_pattern(f'project-path:*{project_group_id}*')
        cache.delete_pattern(f'role-bindings:*{project_group_id}*')
        cache.delete_pattern(f'user-scopes:*{project_group_id}*')
        self._delete_parent_project_group_cache(params['project_group'])

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
            new_project_group_id = params['project_group_id']
            old_project_group_id = project_vo.project_group.project_group_id

            cache.delete_pattern(f'project-path:*{new_project_group_id}*')
            cache.delete_pattern(f'project-path:*{old_project_group_id}*')
            cache.delete_pattern(f'role-bindings:*{new_project_group_id}*')
            cache.delete_pattern(f'role-bindings:*{old_project_group_id}*')
            cache.delete_pattern(f'user-scopes:*{new_project_group_id}*')
            cache.delete_pattern(f'user-scopes:*{old_project_group_id}*')
            self._delete_parent_project_group_cache(params['project_group'])
            self._delete_parent_project_group_cache(project_vo.project_group)

        return project_vo.update(params)

    def delete_project(self, project_id, domain_id):
        project_vo = self.get_project(project_id, domain_id)
        self.delete_project_by_vo(project_vo)

    def delete_project_by_vo(self, project_vo):
        project_group_id = project_vo.project_group_id
        project_vo.delete()

        if project_group_id:
            cache.delete_pattern(f'project-path:*{project_group_id}*')
            cache.delete_pattern(f'project-group-children:*{project_group_id}')
            cache.delete_pattern(f'role-bindings:*{project_group_id}*')
            cache.delete_pattern(f'role-bindings:*:')
            cache.delete_pattern(f'user-scopes:*{project_group_id}*')
            self._delete_parent_project_group_cache(project_vo.project_group)

    def get_project(self, project_id, domain_id, only=None):
        return self.project_model.get(project_id=project_id, domain_id=domain_id, only=only)

    def list_projects(self, query):
        return self.project_model.query(**query)

    def stat_projects(self, query):
        return self.project_model.stat(**query)

    @cache.cacheable(key='project-path:{domain_id}:{project_id}:{project_group_id}', expire=3600)
    def get_project_path(self, project_id, project_group_id, domain_id):
        project_path = []
        if project_id:
            try:
                project_vo = self.get_project(project_id, domain_id)
                project_path = [project_id]
                project_path += self._get_parent_project_group_path(project_vo.project_group, [])
            except Exception as e:
                _LOGGER.debug(f'[get_project_path] Project could not be found. '
                              f'(project_id={project_id}, reason={e})')

        elif project_group_id:
            try:
                project_group_vo = self.project_group_mgr.get_project_group(project_group_id, domain_id)
                project_path = [project_group_id]
                project_path += self._get_parent_project_group_path(project_group_vo.parent_project_group, [])
            except Exception as e:
                _LOGGER.debug(f'[_get_project_path] Project group could not be found. '
                              f'(project_group_id={project_group_id}, reason={e})')

        return project_path

    def _get_parent_project_group_path(self, project_group_vo, project_path):
        project_group_id = project_group_vo.project_group_id
        project_path.append(project_group_id)

        if project_group_vo.parent_project_group:
            project_path = self._get_parent_project_group_path(project_group_vo.parent_project_group, project_path)

        return project_path

    def _delete_parent_project_group_cache(self, project_group_vo):
        cache.delete_pattern(f'project-group-children:*{project_group_vo.project_group_id}')
        if project_group_vo.parent_project_group:
            self._delete_parent_project_group_cache(project_group_vo.parent_project_group)
