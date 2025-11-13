from unittest.mock import Mock, MagicMock, create_autospec
import uuid
import pytest

from clients.spends_client import SpendsHttpClient
from models.config import Envs

from models.spend import Category, Spend, SpendModel
from tests.unit.conftest import spends_generator, category_generator


class SpendDBMock:
    categories: list[Category] = []

    def delete_category(self, ids):
        self.categories = [category for category in self.categories if category.id not in ids]
        SpendsClientMock.categories = [category for category in self.categories if category.id not in ids]

class SpendsClientMock:
    spends: list[SpendModel] = []
    categories: list[Category] = []

    def add_spends(self, spend: SpendModel) -> SpendModel:
        category = Category(name=spend.category.name)
        spend = SpendModel(
            id="1",
            amount=spend.amount,
            description=spend.description,
            spendDate=spend.spendDate,
            currency=spend.currency,
            category=category
        )
        self.spends.append(spend)
        return spend

    def get_spends(self) -> list[SpendModel]:
        return self.spends

    def remove_spends(self, ids: list[str]):
        self.spends = [spend for spend in self.spends if spend.id not in ids]

    def add_category(self, name):
        category = Category(id='1', name=name)
        self.categories.append(category)
        SpendDBMock.categories.append(category)

        return category

@pytest.fixture
def client():
    env_mock = create_autospec(Envs, instance=True)
    env_mock.gateway_url = ''
    c = SpendsHttpClient(env_mock, "")
    c.session = Mock()
    return c

def test_get_categories(client: SpendsHttpClient):
    category_id = uuid.uuid4()
    client.session.get = Mock(
        return_value=Mock(
            json=Mock(
                return_value=[
                    {
                        'id': category_id ,
                        'name': 'test',
                        'username':'test',
                        'archived':False
                    }
                ]
            )
        )
    )
    categories = client.get_categories()
    assert len(categories) == 1
    assert categories == [Category(id=category_id, name='test', username='test', archived=False)]

def test_add_category(client: SpendsHttpClient):
    category_id = uuid.uuid4()
    client.session.post = Mock(
        return_value=Mock(
            json=Mock(
                return_value=
                {
                        'id': category_id,
                        'name': 'test',
                        'username':'test',
                        'archived':False
                    }
            )
        )
    )
    category_obj = client.add_category('test')
    print(category_obj)
    # assert len(category_obj) == 1
    assert category_obj == Category(id=category_id, name='test', username='test', archived=False)

def test_spends_generator():
    spend_client = SpendsClientMock()

    spends_gen = spends_generator(
        spends_client=spend_client,
        spend=SpendModel(
            amount=10,
            description="test",
            category=Category(name='test'),
            spendDate="2021-01-01",
            currency="USD"
        )
    )
    spend = next(spends_gen)
    print(spend)
    assert spend in spend_client.spends

    next(spends_gen, None)

    assert spend not in spend_client.spends

def test_category_generator():
    spend_client = SpendsClientMock()
    spends_db_client = SpendDBMock()

    category_gen = category_generator(
        spends_client=spend_client,
        spend_db=spends_db_client,
        name='test'
    )
    category_obj = next(category_gen)

    assert category_obj in spend_client.categories

    next(category_gen, None)

    assert category_obj not in spend_client.categories

