import allure
import pytest

from models.spend import SpendModel
from models.user import UserData
from utils.test_data_factory import TestDataFactory, logger


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

@pytest.fixture(params=[])
def category(request, spends_client, spend_db):
    yield from category_generator(spends_client, spend_db, request.param)

def category_generator(spends_client, spend_db, name):
    # category_name = request.param
    category = spends_client.add_category(name)
    yield category
    spend_db.delete_category(category.id)


@pytest.fixture(params=[])
def spends(request, spends_client):
    yield from spends_generator(spends_client, request.param)

def spends_generator(spends_client, spend: SpendModel):
    test_spend = spends_client.add_spends(spend)

    # test_spend = spends_client.add_spends(spend_data)

    yield test_spend
    all_spends = spends_client.get_spends()
    if test_spend.id in [spend.id for spend in all_spends]:
        spends_client.remove_spends([test_spend.id])