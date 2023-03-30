import logging
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

from spaceone.core import config, utils
from spaceone.core.manager import BaseManager
from spaceone.identity.connector.smtp_connector import SMTPConnector

_LOGGER = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), f'../template')
JINJA_ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_PATH),
    autoescape=select_autoescape()
)


class EmailManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.smtp_connector: SMTPConnector = self.locator.get_connector('SMTPConnector')

    def send_reset_password_email(self, user_id, email, reset_password_link, language):
        if not os.path.exists(f'{TEMPLATE_PATH}/reset_password_link_{language}.html'):
            language = 'en'

        template = JINJA_ENV.get_template(f'reset_password_link_{language}.html')
        email_contents = template.render(user_name=user_id, reset_password_link=reset_password_link)
        subject = '[SpaceONE] Reset your password'

        self.smtp_connector.send_email(email, subject, email_contents)

    def send_verification_email(self, user_id, email, verification_code, language):
        if not os.path.exists(f'{TEMPLATE_PATH}/reset_password_link_{language}.html'):
            language = 'en'

        template = JINJA_ENV.get_template(f'verification_code_{language}.html')
        email_contents = template.render(user_name=user_id, verification_code=verification_code)
        subject = '[SpaceONE] Verify your email address'

        self.smtp_connector.send_email(email, subject, email_contents)

