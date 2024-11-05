import logging
import random
import pyotp
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

    def set_mfa_options(self, **kwargs):
        pass

    def _load_conf(self):
        identity_conf = config.get_global("IDENTITY") or {}
        mfa_conf = identity_conf.get("mfa", {})
        self.CONST_MFA_VERIFICATION_CODE_TIMEOUT = mfa_conf.get(
            "verify_code_timeout", 300
        )
        self.CONST_MFA_OTP_ISSUER_NAME = config.get_global("MFA_OTP_ISSUER_NAME", "Cloudforet")


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

    def set_mfa_options(self, **kwargs):
        raise NotImplementedError("MFAManager.set_mfa_options not implemented!")

    def create_mfa_verify_code(self, user_id: str, domain_id: str, credentials: dict, user_mfa: dict = None):
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
                    "user_mfa": user_mfa
                },
                expire=self.CONST_MFA_VERIFICATION_CODE_TIMEOUT,
            )
            return verify_code

    @classmethod
    def get_manager_by_mfa_type(cls, mfa_type):
        for subclass in cls.__subclasses__():
            if subclass.mfa_type == mfa_type:
                return subclass()
        raise ERROR_NOT_SUPPORTED_MFA_TYPE(support_mfa_types=["EMAIL", "OTP"])

    def check_mfa_verify_code(self, credentials: dict, verify_code: str) -> bool:
        if cache.is_set():
            ordered_credentials = OrderedDict(sorted(credentials.items()))
            hashed_credentials = utils.dict_to_hash(ordered_credentials)
            cached_mfa_info = cache.get(f"identity:mfa:{hashed_credentials}")
            if self.mfa_type == "OTP":
                otp = self._generate_otp(cached_mfa_info["otp_secret_key"])
                is_verified = otp.verify(verify_code)
            else:
                is_verified = True if cached_mfa_info["verify_code"] == verify_code else False

            if is_verified:
                cache.delete(f"identity:mfa:{hashed_credentials}")
                return True
        raise ERROR_INVALID_VERIFY_CODE(verify_code=verify_code)

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

    @staticmethod
    def _generate_otp(otp_secret_key: str):
        otp = pyotp.TOTP(otp_secret_key)
        return otp

