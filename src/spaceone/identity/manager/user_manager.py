import logging
import re
import pytz
from typing import Tuple
from mongoengine import QuerySet

from spaceone.core.manager import BaseManager

from spaceone.identity.lib.cipher import PasswordCipher
from spaceone.identity.error.error_user import *
from spaceone.identity.model.user.database import User

_LOGGER = logging.getLogger(__name__)


class UserManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = User

    def create_user(self, params: dict) -> User:
        def _rollback(vo: User):
            _LOGGER.info(
                f"[create_user._rollback] Delete user: {vo.user_id} ({vo.name})"
            )
            vo.delete()

        if timezone := params.get("timezone"):
            self._check_timezone(timezone)

        if params["auth_type"] == "EXTERNAL":
            params["password"] = None

        else:
            self._check_user_id_format(params["user_id"])

            if password := params.get("password"):
                self._check_password_format(password)
            else:
                raise ERROR_REQUIRED_PARAMETER(key="password")

            hashed_pw = PasswordCipher().hashpw(password)
            params["password"] = hashed_pw

        params["name"] = params["name"].strip()
        params["email"] = params["email"].strip()

        user_vo = self.user_model.create(params)

        self.transaction.add_rollback(_rollback, user_vo)

        return user_vo

    def update_user_by_vo(self, params: dict, user_vo: User) -> User:
        def _rollback(old_data):
            _LOGGER.info(
                f'[update_user_by_vo._rollback] Revert Data: {old_data["user_id"]}'
            )
            user_vo.update(old_data)

        if timezone := params.get("timezone"):
            self._check_timezone(timezone)

        required_actions = list(user_vo.required_actions)
        is_change_required_actions = False

        if new_password := params.get("password"):
            if PasswordCipher().checkpw(new_password, user_vo.password):
                raise ERROR_PASSWORD_NOT_CHANGED(user_id=user_vo.user_id)

            self._check_password_format(params["password"])
            hashed_pw = PasswordCipher().hashpw(params["password"])
            params["password"] = hashed_pw

            if "UPDATE_PASSWORD" in required_actions:
                required_actions.remove("UPDATE_PASSWORD")
                is_change_required_actions = True

        if is_change_required_actions:
            params["required_actions"] = required_actions

        self.transaction.add_rollback(_rollback, user_vo.to_dict())

        return user_vo.update(params)

    @staticmethod
    def delete_user_by_vo(user_vo: User) -> None:
        user_vo.delete()

    def get_user(self, user_id: str, domain_id: str) -> User:
        return self.user_model.get(user_id=user_id, domain_id=domain_id)

    def filter_users(self, **conditions) -> QuerySet:
        return self.user_model.filter(**conditions)

    def list_users(self, query: dict) -> Tuple[QuerySet, int]:
        return self.user_model.query(**query)

    def stat_users(self, query: dict) -> dict:
        return self.user_model.stat(**query)

    @staticmethod
    def _check_user_id_format(user_id: str) -> None:
        rule = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(rule, user_id):
            raise ERROR_INCORRECT_USER_ID_FORMAT(rule="Email format required.")

    @staticmethod
    def _check_password_format(password: str) -> None:
        if len(password) < 8:
            raise ERROR_INCORRECT_PASSWORD_FORMAT(rule="At least 9 characters long.")
        elif not re.search("[a-z]", password):
            raise ERROR_INCORRECT_PASSWORD_FORMAT(
                rule="Contains at least one lowercase character"
            )
        elif not re.search("[A-Z]", password):
            raise ERROR_INCORRECT_PASSWORD_FORMAT(
                rule="Contains at least one uppercase character"
            )
        elif not re.search("[0-9]", password):
            raise ERROR_INCORRECT_PASSWORD_FORMAT(rule="Contains at least one number")

    @staticmethod
    def _check_timezone(timezone):
        if timezone not in pytz.all_timezones:
            raise ERROR_INVALID_PARAMETER(key="timezone", reason="Timezone is invalid.")
