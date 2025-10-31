import json
import os
from urllib.parse import urljoin

import allure
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from pytest import FixtureDef, FixtureRequest
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


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item):
    yield
    allure.dynamic.title(" ".join(item.name.split('_')[1:]).title())

def allure_logger(config) -> AllureReporter:
    listener: AllureListener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger

@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request):
    yield
    logger = allure_logger(request.config)
    item = logger.get_last_item()
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}]" + " ".join(fixturedef.argname.split('_')).title()



@pytest.fixture(scope="session", autouse=True)
@allure.step('Loading environment config')
def envs() -> Envs:
    load_dotenv()
    envs_instance = Envs(
        frontend_url=os.getenv('FRONTEND_URL'),
        gateway_url=os.getenv('GATEWAY_URL'),
        register_url=os.getenv('REGISTER_URL'),
        auth_url=os.getenv('AUTH_URL'),
        spend_db_url=os.getenv('SPEND_DB_URL'),
        userdata_db_url=os.getenv('USERDATA_DB_URL'),
        test_username=os.getenv('TEST_USERNAME'),
        test_password=os.getenv('TEST_PASSWORD')
    )

    safe_envs = envs_instance.get_safe_dict_for_log()
    allure.attach(json.dumps(safe_envs, indent=2), name='envs.json', attachment_type=AttachmentType.JSON)

    # allure.attach(envs_instance.model_dump_json(indent=2), name= 'envs.json', attachment_type=AttachmentType.JSON)

    return envs_instance

@pytest.fixture(scope="session")
@allure.step('Getting API user')
def api_user(envs):
    # return os.getenv('TEST_USERNAME'), os.getenv('TEST_PASSWORD')
    return 'Lamaw', 'Lamaw2002'

@pytest.fixture(scope="function")
def register(envs, random_user):
    username, password = random_user.username, random_user.password
    with allure.step('Opening registration page'):
        browser.open(envs.register_url)
    with allure.step('Entering username: ' + username):
        browser.element("[name=username]").type(username)
    with allure.step('Entering password: ' + password):
        browser.element("[name=password]").type(password)
    with allure.step('Entering submit password: ' + password):
        browser.element("[name=passwordSubmit]").type(password)
    with allure.step('Submit registration'):
        browser.element('button.form__submit').click()

    token = browser.driver.execute_script('return window.localStorage.getItem("id_token")')
    try:
        allure.attach(token, name='token.txt', attachment_type=AttachmentType.TEXT)
    except TypeError:
        pass
    return token

@pytest.fixture(scope="function")
def register_with_different_passwords(envs, random_user):
    username, password = random_user.username, random_user.password
    with allure.step('Opening registration page'):
        browser.open(envs.register_url)
    with allure.step('Entering username: ' + username):
        browser.element("[name=username]").type(username)
    with allure.step('Entering password: ' + password):
        browser.element("[name=password]").type(password)
    with allure.step('Entering incorrect submit password: ' + password+'_1'):
        browser.element("[name=passwordSubmit]").type(f"{random_user.password}_1")
    with allure.step('Submit registration'):
        browser.element('button.form__submit').click()

@pytest.fixture(scope="function")
def auth_with_wrong_password(envs, random_user):
    username, password = random_user.username, random_user.password
    with allure.step('Opening authorization page'):
        browser.open(envs.auth_url)
    with allure.step('Entering username: ' + username):
        browser.element("[name=username]").type(username)
    with allure.step('Entering password: ' + password):
        browser.element("[name=password]").type(password)
    with allure.step('Submit authorization'):
        browser.element('button.form__submit').click()


@pytest.fixture(scope="session")
def auth(envs, api_user):
    username, password = api_user
    with allure.step('Opening authorization page'):
        browser.open(envs.auth_url)
    with allure.step('Entering username: ' + username):
        browser.element("[name=username]").type(username)
    with allure.step('Entering password: ' + password):
        browser.element("[name=password]").type(password)
    with allure.step('Submit authorization'):
        browser.element('button.form__submit').click()
    try:
        with allure.step('Check is user registered'):
            browser.element(by.id("spendings")).should(be.visible)

    except Exception as e:
        with allure.step('User is not registered \n\n Opening registration page'):
            browser.open(envs.register_url)
        with allure.step('Entering username: ' + username):
            browser.element("[name=username]").type(username)
        with allure.step('Entering password: ' + password):
            browser.element("[name=password]").type(password)
        with allure.step('Entering submit password: ' + password):
            browser.element("[name=passwordSubmit]").type(password)
        with allure.step('Submit registration'):
            browser.element('button.form__submit').click()

    token = browser.driver.execute_script('return window.localStorage.getItem("id_token")')
    allure.attach(token, name='token.txt', attachment_type=AttachmentType.TEXT)
    return token

@pytest.fixture()
@allure.step('Opening main page')
def main_page(auth, envs):
    browser.open(envs.frontend_url)

@pytest.fixture()
@allure.step('Opening profile page')
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

