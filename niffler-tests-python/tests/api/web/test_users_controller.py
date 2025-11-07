import pytest
import allure

from marks import Pages, TestData


@allure.epic("niffler-userdata")
@allure.feature("User profile")
class TestUsersController:

    @allure.story("Updating User profile")
    @TestData.update_profile({
        'currency': 'KZT'
    })
    @TestData.get_user_data_from_db('Lamaw')
    def test_update_profile_currency_and_check_db(self, update_profile, get_user_data_from_db):
        assert get_user_data_from_db.currency == update_profile.currency

    @allure.story("Updating User profile")
    @TestData.update_profile({
        'fullname': '555'
    })
    @TestData.get_user_data_from_db('Lamaw')
    def test_update_profile_fullname_and_check_db(self, update_profile, get_user_data_from_db):
        assert get_user_data_from_db.full_name == update_profile.fullname