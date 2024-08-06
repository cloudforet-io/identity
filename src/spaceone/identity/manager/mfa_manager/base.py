import logging
import random
from abc import abstractmethod, ABC, ABCMeta
from collections import OrderedDict

from spaceone.core import config, utils, cache
from spaceone.core.manager import BaseManager

from spaceone.identity.error.error_authentication import ERROR_INVALID_CREDENTIALS
from spaceone.identity.error.error_mfa import ERROR_NOT_SUPPORTED_MFA_TYPE
from spaceone.identity.error.error_user import ERROR_INVALID_VERIFY_CODE

__all__ = ["BaseMFAManager", "MFAManager"]
_LOGGER = logging.getLogger(__name__)


class BaseMFAManager(BaseManager, ABC):
    @abstractmethod
    def enable_mfa(self, **kwargs):
        pass

    @abstractmethod
    def disable_mfa(self, **kwargs):
        pass

    def confirm_mfa(self, **kwargs):
        pass

    def _load_conf(self):
        identity_conf = config.get_global("IDENTITY") or {}
        mfa_conf = identity_conf.get("mfa", {})
        self.CONST_MFA_VERIFICATION_CODE_TIMEOUT = mfa_conf.get(
            "verify_code_timeout", 300
        )


class MFAManager(BaseMFAManager, metaclass=ABCMeta):
    mfa_type: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_conf()

    def enable_mfa(self, **kwargs):
        raise NotImplementedError("MFAManager.enable_mfa not implemented!")

    def disable_mfa(self, **kwargs):
        raise NotImplementedError("MFAManager.disable_mfa not implemented!")

    def confirm_mfa(self, **kwargs):
        raise NotImplementedError("MFAManager.confirm_mfa not implemented!")

    def create_mfa_verify_code(self, user_id: str, domain_id: str, credentials: dict):
        if cache.is_set():
            verify_code = self._generate_verify_code()
            ordered_credentials = OrderedDict(sorted(credentials.items()))
            hashed_credentials = utils.dict_to_hash(ordered_credentials)
            cache.delete(f"identity:mfa:{hashed_credentials}")
            cache.set(
                f"identity:mfa:{hashed_credentials}",
                {
                    "verify_code": verify_code,
                    "user_id": user_id,
                    "domain_id": domain_id,
                },
                expire=self.CONST_MFA_VERIFICATION_CODE_TIMEOUT,
            )
            return verify_code

    @classmethod
    def get_manager_by_mfa_type(cls, mfa_type):
        for subclass in cls.__subclasses__():
            if subclass.mfa_type == mfa_type:
                return subclass()
        raise ERROR_NOT_SUPPORTED_MFA_TYPE(support_mfa_types=["EMAIL"])

    @staticmethod
    def check_mfa_verify_code(credentials: dict, verify_code: str) -> bool:
        if cache.is_set():
            ordered_credentials = OrderedDict(sorted(credentials.items()))
            hashed_credentials = utils.dict_to_hash(ordered_credentials)
            cached_mfa_info = cache.get(f"identity:mfa:{hashed_credentials}")
            if cached_mfa_info["verify_code"] == verify_code:
                cache.delete(f"identity:mfa:{hashed_credentials}")
                return True
        raise ERROR_INVALID_VERIFY_CODE(verify_code=credentials["verify_code"])

    @staticmethod
    def get_mfa_info(credentials: dict):
        if cache.is_set():
            ordered_credentials = OrderedDict(sorted(credentials.items()))
            hashed_credentials = utils.dict_to_hash(ordered_credentials)
            cached_mfa_info = cache.get(f"identity:mfa:{hashed_credentials}")
            return cached_mfa_info
        raise ERROR_INVALID_CREDENTIALS()

    @staticmethod
    def _generate_verify_code():
        return str(random.randint(100000, 999999))
