from selene import browser
from selene import have, by, be

from marks import Pages, TestData


class TestProfilePage:

    @Pages.profile_page
    def test_username_from_api_equals_to_frontend_username(self, get_user_profile):
        browser.element(by.id('username')).should(have.value(get_user_profile['username']))

    @Pages.profile_page
    @TestData.update_profile({
        'fullname': '7777'
    })
    def test_update_profile(self, get_user_profile, update_profile):
        browser.open('http://frontend.niffler.dc/profile')
        browser.element(by.id('name')).should(have.no.value(get_user_profile['fullname']))

    @Pages.profile_page
    @TestData.update_profile({
        'fullname': '555'
    })
    @TestData.get_user_data_from_db('Lamaw')
    def test_update_profile_fullname_and_check_db(self, update_profile, get_user_data_from_db):
        assert get_user_data_from_db.full_name == update_profile.fullname

    @Pages.profile_page
    @TestData.update_profile({
        'currency': 'KZT'
    })
    @TestData.get_user_data_from_db('Lamaw')
    def test_update_profile_and_check_db(self, update_profile, get_user_data_from_db):
        assert get_user_data_from_db.currency == update_profile.currency

