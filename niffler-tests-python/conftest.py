import os
from urllib.parse import urljoin

from selene import have, by, be
from selene.support.shared import browser
import pytest

from dotenv import load_dotenv
from selenium.common import NoSuchElementException
from trio import current_effective_deadline

from clients.users_client import UsersHttpClient
from database.spend_db import SpendDB
from database.userdata_db import UserDataDB
from e2e.web.conftest import random_user

from clients.spends_client import SpendsHttpClient
from models.config import Envs
from models.spend import Category
from models.userdata import UserModel, User


@pytest.fixture(scope="session", autouse=True)
def envs() -> Envs:
    load_dotenv()
    return Envs(
        frontend_url=os.getenv('FRONTEND_URL'),
        gateway_url=os.getenv('GATEWAY_URL'),
        register_url=os.getenv('REGISTER_URL'),
        auth_url=os.getenv('AUTH_URL'),
        spend_db_url=os.getenv('SPEND_DB_URL'),
        userdata_db_url=os.getenv('USERDATA_DB_URL'),
        test_username=os.getenv('TEST_USERNAME'),
        test_password=os.getenv('TEST_PASSWORD')
    )

@pytest.fixture(scope="session")
def api_user(envs):
    # return os.getenv('TEST_USERNAME'), os.getenv('TEST_PASSWORD')
    return 'Lamaw', 'Lamaw2002'

@pytest.fixture(scope="function")
def register(envs, random_user):
    username, password = random_user.username, random_user.password
    browser.open(envs.register_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element("[name=passwordSubmit]").type(password)
    browser.element('button.form__submit').click()

    return browser.driver.execute_script('return window.localStorage.getItem("id_token")')

@pytest.fixture(scope="function")
def register_with_different_passwords(envs, random_user):
    username, password = random_user.username, random_user.password
    browser.open(envs.register_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element("[name=passwordSubmit]").type(f"{random_user.password}_1")
    browser.element('button.form__submit').click()


@pytest.fixture(scope="function")
def auth_with_wrong_password(envs, random_user):
    username, password = random_user.username, random_user.password
    browser.open(envs.auth_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element('button.form__submit').click()


@pytest.fixture(scope="session")
def auth(envs, api_user):
    username, password = api_user
    browser.open(envs.frontend_url)
    browser.element("[name=username]").type(username)
    browser.element("[name=password]").type(password)
    browser.element('button.form__submit').click()
    try:
        browser.element(by.id("spendings")).should(be.visible)

    except Exception as e:
        browser.open(envs.register_url)
        browser.element("[name=username]").type(username)
        browser.element("[name=password]").type(password)
        browser.element("[name=passwordSubmit]").type(password)
        browser.element('button.form__submit').click()

    return browser.driver.execute_script('return window.localStorage.getItem("id_token")')

@pytest.fixture()
def main_page(auth, envs):
    browser.open(envs.frontend_url)

@pytest.fixture()
def profile_page(auth, envs):
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
def auth_page(auth, envs):
    ...

@pytest.fixture(scope="session")
def spends_client(envs, auth) -> SpendsHttpClient:
    return SpendsHttpClient(envs.gateway_url, auth)

@pytest.fixture(scope="session")
def users_client(envs, auth) -> UsersHttpClient:
    return UsersHttpClient(envs.gateway_url, auth)

@pytest.fixture(params=[])
def update_profile(request, users_client):
    profile = users_client.update_user(request.param)
    yield profile
    users_client.update_user({'fullname': '6666'})
    users_client.update_user({'currency': 'RUB'})

@pytest.fixture()
def get_user_profile(users_client):
    profile = users_client.get_current_user()
    return profile

@pytest.fixture(scope="session")
def spend_db(envs) -> SpendDB:
    return SpendDB(envs.spend_db_url)

@pytest.fixture(scope="session")
def userdata_db(envs) -> UserDataDB:
    return UserDataDB(envs.userdata_db_url)


@pytest.fixture(params=[])
def category(request, spends_client, spend_db):
    category_name = request.param
    category = spends_client.add_category(category_name)
    yield category_name
    spend_db.delete_category(category.id)

@pytest.fixture(params=[])
def get_user_data_from_db(request, userdata_db) -> User:
    username = request.param
    user_data = userdata_db.get_user_data(username)
    return User.model_validate(user_data)

@pytest.fixture(params=[])
def spends(request, spends_client):
    spend_data = request.param

    test_spend = spends_client.add_spends(spend_data)

    yield test_spend
    all_spends = spends_client.get_spends()
    if test_spend.id in [spend.id for spend in all_spends]:
        spends_client.remove_spends([test_spend.id])

