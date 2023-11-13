import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from spaceone.core import config
from spaceone.identity.connector.smtp_connector import SMTPConnector
from spaceone.identity.manager.mfa_manager import MFAManager

_LOGGER = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), f'../../template')
JINJA_ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_PATH),
    autoescape=select_autoescape()
)


LANGUAGE_MAPPER = {
    'default': {
        'reset_password': 'Reset your password',
        'temp_password': 'Your password has been changed',
        'verify_email': 'Verify your notification email',
    },
    'ko': {
        'reset_password': '비밀번호 재설정 안내',
        'temp_password': '임시 비밀번호 발급 안내',
        'verify_email': '알림전용 이메일 계정 인증 안내',
    },
    'en': {
        'reset_password': 'Reset your password',
        'temp_password': 'Your password has been changed',
        'verify_email': 'Verify your notification email',
    },
    'ja': {
        'reset_password': 'パスワードリセットのご案内',
        'temp_password': '仮パスワード発行のご案内',
        'verify_email': '通知メールアカウント認証のご案内',
    }

}


class EmailMFAManager(MFAManager):
    mfa_type = 'EMAIL'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smtp_connector: SMTPConnector = self.locator.get_connector('SMTPConnector')

    def enable_mfa(self, user_id, domain_id, user_mfa, language):
        self.send_mfa_verify_email(user_id, domain_id, user_mfa['options'].get('email'), language)

    def disable_mfa(self, user_id, domain_id, user_mfa, language):
        self.send_mfa_verify_email(user_id, domain_id, user_mfa['options'].get('email'), language)

    def confirm_mfa(self, user_id, domain_id, verify_code):
        return self.check_mfa_verify_code(user_id, domain_id, verify_code)

    def send_mfa_verify_email(self, user_id, domain_id, email, language):
        service_name = self._get_service_name()
        language_map_info = LANGUAGE_MAPPER.get(language, 'default')
        verify_code = self.create_mfa_verify_code(user_id, domain_id)

        template = JINJA_ENV.get_template(f'verification_code_{language}.html')
        email_contents = template.render(user_name=user_id, verification_code=verify_code,
                                         service_name=service_name)
        subject = f'[{service_name}] {language_map_info["verify_email"]}'

        self.smtp_connector.send_email(email, subject, email_contents)

    @staticmethod
    def _get_service_name():
        return config.get_global('EMAIL_SERVICE_NAME')
