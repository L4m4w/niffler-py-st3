import pytest

from clients.spends_client import SpendsHttpClient
from clients.users_client import UsersHttpClient
from database.spend_db import SpendDB
from database.userdata_db import UserDataDB
from models.spend import Category
from models.userdata import User


@pytest.fixture(scope="session")
def spends_client(envs, auth_front_token) -> SpendsHttpClient:
    return SpendsHttpClient(envs, auth_front_token)


@pytest.fixture(scope="session")
def users_client(envs, auth_front_token) -> UsersHttpClient:
    return UsersHttpClient(envs, auth_front_token)


@pytest.fixture(scope="session")
def spend_db(envs) -> SpendDB:
    return SpendDB(envs)


@pytest.fixture(scope="session")
def userdata_db(envs) -> UserDataDB:
    return UserDataDB(envs)


@pytest.fixture(params=[])
def update_profile(request, users_client: UsersHttpClient):
    profile = users_client.update_user(request.param)
    yield profile
    users_client.update_user({'fullname': '6666'})
    users_client.update_user({'currency': 'RUB'})


@pytest.fixture()
def get_user_profile(users_client: UsersHttpClient):
    profile = users_client.get_current_user()
    return profile


@pytest.fixture(params=[])
def get_user_data_from_db(request, userdata_db: UserDataDB) -> User:
    username = request.param
    user_data = userdata_db.get_user_data(username)
    return User.model_validate(user_data)

@pytest.fixture(params=[])
def get_category_data_from_db(request, spend_db: SpendDB) -> Category:
    username = request.param
    category_data = spend_db.get_user_categories(username)
    # return [Category.model_validate(item) for item in category_data]
    return category_data[0]

