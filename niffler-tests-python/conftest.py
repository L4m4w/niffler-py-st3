import json
import os

import allure
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from pytest import FixtureDef
from selene import by, be
from selene.support.shared import browser
import pytest

from dotenv import load_dotenv

from tests.e2e.web.conftest import random_user
from fixtures.auth_fixtures import api_user

from models.config import Envs

pytest_plugins=['fixtures.auth_fixtures', 'fixtures.client_fixtures', 'fixtures.pages_fixtures']

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
        auth_secret=os.getenv('AUTH_SECRET'),
        spend_db_url=os.getenv('SPEND_DB_URL'),
        userdata_db_url=os.getenv('USERDATA_DB_URL'),
        test_username=os.getenv('TEST_USERNAME'),
        test_password=os.getenv('TEST_PASSWORD')
    )

    safe_envs = envs_instance.get_safe_dict_for_log()
    allure.attach(json.dumps(safe_envs, indent=2), name='envs.json', attachment_type=AttachmentType.JSON)

    # allure.attach(envs_instance.model_dump_json(indent=2), name= 'envs.json', attachment_type=AttachmentType.JSON)

    return envs_instance


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
def auth_front_token(envs: Envs, api_user):
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
#
# @pytest.fixture(scope="session")
# def auth_front_token(envs: Envs):
#     browser.open(envs.frontend_url)
#     browser.element('a[href*=redirect]').click()
#     browser.element('input[name=username]').set_value(envs.test_username)
#     browser.element('input[name=password]').set_value(envs.test_password)
#     browser.element('button[type=submit]').click()
#     token = browser.driver.execute_script('return window.sessionStorage.getItem("id_token")')
#     allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
#     return token


