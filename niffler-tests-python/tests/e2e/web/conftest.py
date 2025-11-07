import logging
from wsgiref.util import application_uri

import allure
import pytest
from pytest import Parser  # noqa: PT013
from selene.support.shared import browser
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from models.user import UserData
from pages.application import app
from utils.test_data_factory import TestDataFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def browser_management(request):


    chrome_options = Options()

    # Обязательные опции для работы в CI/контейнерах
    # chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # Дополнительные опции для стабильности
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--remote-debugging-port=9222')

    # Установка опций для Selene
    browser.config.driver_options = chrome_options
    browser.config.timeout = 10
    # browser.config.base_url = base_url

    yield browser

    browser.quit()


@pytest.fixture(autouse=True, scope="class")
def api_config(request):
    if request.cls:
        setattr(request.cls, 'FRONTEND_URL', "http://frontend.niffler.dc/")
        setattr(request.cls, 'AUTH_URL', "http://auth.niffler.dc:9000/")

@pytest.fixture(scope="function")
def data_factory():
    factory = TestDataFactory()
    logger.info("Test data factory initialized")

    yield factory

    stats = factory.get_generation_stats()
    logger.info(f"Test data generation stats: {stats}")

@pytest.fixture(scope='function')
@allure.step('Creating random user credentials (username, password)')
def random_user(data_factory) -> UserData:
    return data_factory.create_user_credentials_data()

@pytest.fixture(scope='function')
def register_user(random_user):
    username, password = random_user.username, random_user.password
    app.register_page.open()
    app.register_page.registration(username, password)
    assert app.register_page.check_registration_status()
    return username, password


@pytest.fixture(params=[])
def category(request, spends_client, spend_db):
    category_name = request.param
    category = spends_client.add_category(category_name)
    yield category_name
    spend_db.delete_category(category.id)


@pytest.fixture(params=[])
def spends(request, spends_client):
    spend_data = request.param

    test_spend = spends_client.add_spends(spend_data)

    yield test_spend
    all_spends = spends_client.get_spends()
    if test_spend.id in [spend.id for spend in all_spends]:
        spends_client.remove_spends([test_spend.id])
