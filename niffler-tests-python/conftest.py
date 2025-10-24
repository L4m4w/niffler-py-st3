import os
from urllib.parse import urljoin

from selene import have, by, be
from selene.support.shared import browser
import pytest

from dotenv import load_dotenv
from selenium.common import NoSuchElementException
from trio import current_effective_deadline

from clients.users_client import UsersHttpClient
from e2e.web.conftest import random_user

from clients.spends_client import SpendsHttpClient


@pytest.fixture(scope="session", autouse=True)
def envs():
    load_dotenv()

@pytest.fixture(scope="session")
def frontend_url(envs):
    return os.getenv('FRONTEND_URL')

@pytest.fixture(scope="session")
def register_url(envs):
    return os.getenv('REGISTER_URL')

@pytest.fixture(scope="session")
def auth_url(envs):
    return os.getenv('AUTH_URL')

@pytest.fixture(scope="session")
def gateway_url(envs):
    return os.getenv('GATEWAY_URL')

@pytest.fixture(scope="session")
def api_user(envs):
    # return os.getenv('TEST_USERNAME'), os.getenv('TEST_PASSWORD')
    return 'Lamaw1234', 'Lamaw20021'

@pytest.fixture(scope="function")
def register(register_url, random_user):
    username, password = random_user.username, random_user.password
    browser.open(register_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element("[name=passwordSubmit]").type(password)
    browser.element('button.form__submit').click()

    return browser.driver.execute_script('return window.localStorage.getItem("id_token")')

@pytest.fixture(scope="function")
def register_with_different_passwords(register_url, random_user):
    username, password = random_user.username, random_user.password
    browser.open(register_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element("[name=passwordSubmit]").type(f"{random_user.password}_1")
    browser.element('button.form__submit').click()


@pytest.fixture(scope="function")
def auth_with_wrong_password(auth_url, random_user):
    username, password = random_user.username, random_user.password
    browser.open(auth_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element('button.form__submit').click()


@pytest.fixture(scope="session")
def auth(frontend_url, register_url, api_user):
    username, password = api_user
    browser.open(frontend_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element('button.form__submit').click()
    try:
        browser.element(by.id("spendings")).should(be.visible)

    except Exception as e:
        browser.open(register_url)
        browser.element("[name=username]").type(username)
        browser.element("[name=password]").type(password)
        browser.element("[name=passwordSubmit]").type(password)
        browser.element('button.form__submit').click()

    return browser.driver.execute_script('return window.localStorage.getItem("id_token")')

@pytest.fixture()
def main_page(auth, frontend_url):
    browser.open(frontend_url)

@pytest.fixture()
def profile_page(auth, frontend_url):
    browser.open(urljoin(frontend_url, '/profile'))

@pytest.fixture()
def registration_page(register, register_url):
    ...

@pytest.fixture()
def registration_page_with_different_passwords(register_with_different_passwords, register_url):
    ...

@pytest.fixture()
def auth_page_with_wrong_password(auth_with_wrong_password, auth_url):
    ...

@pytest.fixture()
def auth_page(auth, auth_url):
    ...

@pytest.fixture(scope="session")
def spends_client(gateway_url, auth) -> SpendsHttpClient:
    return SpendsHttpClient(gateway_url, auth)

@pytest.fixture(scope="session")
def users_client(gateway_url, auth) -> UsersHttpClient:
    return UsersHttpClient(gateway_url, auth)

@pytest.fixture(params=[])
def update_profile_name(request, users_client):
    profile = users_client.update_user(request.param)
    yield profile
    users_client.update_user({'fullname': '6666'})

@pytest.fixture()
def get_user_profile(users_client):
    profile = users_client.get_current_user()
    return profile

@pytest.fixture(params=[])
def category(request, spends_client):
    category_name = request.param
    current_categories = spends_client.get_categories()
    current_category_names = [category["name"] for category in current_categories]
    if category_name not in current_category_names:
        spends_client.add_category(category_name)

@pytest.fixture(params=[])
def spends(request, spends_client):
    spend = spends_client.add_spends(request.param)
    yield spend
    try:
        spends_client.remove_spends([spend['id']])
    except Exception:
        ...

