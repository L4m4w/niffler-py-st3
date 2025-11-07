from urllib.parse import urljoin

import allure
import pytest
from selene.support.shared import browser


@pytest.fixture()
@allure.step('Opening main page')
def main_page(auth_front_token, envs):
    browser.open(envs.frontend_url)


@pytest.fixture()
@allure.step('Opening profile page')
def profile_page(auth_front_token, envs):
    browser.open(urljoin(envs.frontend_url, '/profile'))


@pytest.fixture()
def registration_page(register, envs):
    ...


@pytest.fixture()
def registration_page_with_different_passwords(register_with_different_passwords, envs):
    ...


@pytest.fixture()
def auth_page_with_wrong_password(auth_with_wrong_password, envs):
    ...


@pytest.fixture()
def auth_page(auth_front_token, envs):
    ...
