import logging
from typing import Union

from spaceone.core.service import *
from spaceone.core.service.utils import *
from spaceone.identity.error import *

from spaceone.identity.manager.package_manager import PackageManager
from spaceone.identity.manager.opsflow_manager import OpsflowManager
from spaceone.identity.model.package.request import *
from spaceone.identity.model.package.response import *

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class PackageService(BaseService):
    resource = "Package"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.package_mgr = PackageManager()

    @transaction(permission="identity:Package.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def create(self, params: PackageCreateRequest) -> Union[PackageResponse, dict]:
        """Create package
        Args:
            params (dict): {
                'name': 'str',          # required
                'description': 'str',
                'tags': 'dict',         # required
                'domain_id': 'str'      # injected from auth (required)
            }
        """

        params_dict = params.dict()
        params_dict["order"] = self._get_highest_order(params.domain_id) + 1

        package_vo = self.package_mgr.create_package(params_dict)
        return PackageResponse(**package_vo.to_dict())

    @transaction(permission="identity:Package.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def update(self, params: PackageUpdateRequest) -> Union[PackageResponse, dict]:
        """Update package
        Args:
            params (dict): {
                'package_id': 'str', # required
                'name': 'str',
                'description': 'str',
                'tags': 'dict',
                'domain_id': 'str'      # injected from auth (required)
            }
        """
        package_vo = self.package_mgr.get_package(
            params.package_id,
            params.domain_id,
        )

        package_vo = self.package_mgr.update_package_by_vo(
            params.dict(exclude_unset=True), package_vo
        )

        return PackageResponse(**package_vo.to_dict())

    @transaction(permission="identity:Package.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def delete(self, params: PackageDeleteRequest) -> None:
        """Delete package
        Args:
            params (dict): {
                'package_id': 'str',    # required
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            None
        """

        package_vo = self.package_mgr.get_package(
            params.package_id,
            params.domain_id,
        )

        if package_vo.is_default:
            raise ERROR_INVALID_PARAMETER(
                key="package_id",
                reason=f"Cannot delete default package.",
            )

        self._check_existence_of_task_category(params.domain_id, params.package_id)

        self.package_mgr.delete_package_by_vo(package_vo)

    @transaction(permission="identity:Package.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def set_default(
        self, params: PackageSetDefaultRequest
    ) -> Union[PackageResponse, dict]:
        """Set default package
        Args:
            params (dict): {
                'package_id': 'str',     # required
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            PackageResponse:
        """
        package_vos = self.package_mgr.filter_packages(domain_id=params.domain_id)
        for package_vo in package_vos:
            if package_vo.package_id == params.package_id:
                self.package_mgr.update_package_by_vo({"is_default": True}, package_vo)
            else:
                self.package_mgr.update_package_by_vo({"is_default": False}, package_vo)

        package_vo = self.package_mgr.get_package(
            params.package_id,
            params.domain_id,
        )

        return PackageResponse(**package_vo.to_dict())

    @transaction(permission="identity:Package.write", role_types=["DOMAIN_ADMIN"])
    @convert_model
    def change_order(
        self, params: PackageChangeOrderRequest
    ) -> Union[PackageResponse, dict]:
        """Change order of package
        Args:
            params (dict): {
                'package_id': 'str',        # required
                'order': 'int',             # required
                'domain_id': 'str'          # injected from auth (required)
            }
        Returns:
            PackageResponse:
        """

        package_vo = self.package_mgr.get_package(
            params.package_id,
            params.domain_id,
        )

        self._check_order(params.order, params.domain_id)

        new_order = params.order
        old_order = package_vo.order

        if new_order > old_order:
            package_vos = self.package_mgr.filter_packages(domain_id=params.domain_id)
            for package_vo in package_vos:
                if params.package_id == package_vo.package_id:
                    package_vo.update({"order": new_order})
                elif old_order < package_vo.order <= new_order:
                    package_vo.update({"order": package_vo.order - 1})

        if new_order < old_order:
            package_vos = self.package_mgr.filter_packages(domain_id=params.domain_id)
            for package_vo in package_vos:
                if params.package_id == package_vo.package_id:
                    package_vo.update({"order": new_order})
                elif new_order <= package_vo.order < old_order:
                    package_vo.update({"order": package_vo.order + 1})

        package_vo = self.package_mgr.get_package(
            params.package_id,
            params.domain_id,
        )

        return PackageResponse(**package_vo.to_dict())

    @transaction(
        permission="identity:Package.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @convert_model
    def get(self, params: PackageGetRequest) -> Union[PackageResponse, dict]:
        """Get package
        Args:
            params (dict): {
                'package_id': 'str',    # required
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            PackageResponse:
        """

        package_vo = self.package_mgr.get_package(
            params.package_id,
            params.domain_id,
        )
        return PackageResponse(**package_vo.to_dict())

    @transaction(
        permission="identity:Package.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(
        [
            "package_id",
            "name",
            "domain_id",
        ]
    )
    @append_keyword_filter(["package_id", "name"])
    @convert_model
    def list(self, params: PackageSearchQueryRequest) -> Union[PackagesResponse, dict]:
        """List packages
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'package_id': 'str',
                'name': 'str',
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            PackagesResponse:
        """

        query = params.query or {}
        package_vos, total_count = self.package_mgr.list_packages(
            query, params.domain_id
        )

        packages_info = [package_vo.to_dict() for package_vo in package_vos]
        return PackagesResponse(results=packages_info, total_count=total_count)

    @transaction(
        permission="identity:Package.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @append_query_filter(["domain_id"])
    @append_keyword_filter(["package_id", "name"])
    @convert_model
    def stat(self, params: PackageStatQueryRequest) -> dict:
        """Stat packages
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'domain_id': 'str'      # injected from auth (required)
            }
        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.query or {}
        return self.package_mgr.stat_package(query)

    def _check_order(self, order: int, domain_id: str) -> None:
        if order <= 0:
            raise ERROR_INVALID_PARAMETER(
                key="order", reason="The order must be greater than 0."
            )

        highest_order = self._get_highest_order(domain_id)
        if order > highest_order:
            raise ERROR_INVALID_PARAMETER(
                key="order",
                reason="The order is out of range.",
            )

    def _get_highest_order(self, domain_id: str):
        package_vos = self.package_mgr.filter_packages(domain_id=domain_id)

        return package_vos.count()

    @staticmethod
    def _check_existence_of_task_category(domain_id: str, package_id: str):
        opsflow_mgr = OpsflowManager()
        response = opsflow_mgr.list_task_categories_by_package(domain_id, package_id)
        total_count = response.get("total_count", 0)

        if total_count > 0:
            categories_info = response.get("results", [])
            existing_categories = [
                category_info["category_id"] for category_info in categories_info
            ]

            if existing_categories:
                raise ERROR_EXIST_RESOURCE(
                    child="Package",
                    parent=f"TaskCategory({', '.join(existing_categories)})",
                )
