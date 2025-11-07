import allure
import pytest
from allure_commons.types import AttachmentType

from clients.oauth_client import OAuthClient
from models.config import Envs


@pytest.fixture(scope="session")
def auth_api_token(envs: Envs):
    token = OAuthClient(envs).get_token(envs.test_username, envs.test_password)
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token


@pytest.fixture(scope="session")
@allure.step('Getting API user')
def api_user(envs):
    # return os.getenv('TEST_USERNAME'), os.getenv('TEST_PASSWORD')
    return 'Lamaw', 'Lamaw2002'
