import logging
import random
from abc import abstractmethod, ABC, ABCMeta

from spaceone.core import config, utils, cache
from spaceone.core.manager import BaseManager

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
        mfa_conf = identity_conf.get("token", {})
        self.CONST_MFA_VERIFICATION_CODE_TIMEOUT = mfa_conf.get(
            "mfa_verify_code_timeout", 300
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

    def create_mfa_verify_code(self, user_id, domain_id):
        if cache.is_set():
            verify_code = self._generate_verify_code()
            cache.delete(f"mfa-verify-code:{domain_id}:{user_id}")
            cache.set(
                f"mfa-verify-code:{domain_id}:{user_id}",
                verify_code,
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
    def check_mfa_verify_code(user_id, domain_id, verify_code):
        if cache.is_set():
            cached_verify_code = cache.get(f"mfa-verify-code:{domain_id}:{user_id}")
            if cached_verify_code == verify_code:
                cache.delete(f"mfa-verify-code:{domain_id}:{user_id}")
                return True
        raise ERROR_INVALID_VERIFY_CODE(verify_code=verify_code)

    @staticmethod
    def _generate_verify_code():
        return str(random.randint(100000, 999999))
