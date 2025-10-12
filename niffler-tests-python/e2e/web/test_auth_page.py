import os
import shutil

import allure
from allure_commons.types import Severity
from selene.support.shared import browser
import pytest

# from utils.utils_pages.utils_account import login_ui
from pages.application import app


class TestAuthApp:

    def test_successful_login(self, test_data, register_user):
        username, password = register_user
        app.login_page.open()
        app.login_page.login(username, password)
        assert app.login_page.check_login_status()

    def test_successful_registration(self, test_data):
        app.register_page.open()
        app.register_page.registration(**test_data['user_data'][0])
        assert app.register_page.check_registration_status()

    def test_login_invalid_password_error(self, test_data):
        username, password = test_data['user_data'][0]['username'], test_data['user_data'][0]['password']
        app.login_page.open()
        app.login_page.login(username, password)
        app.login_page.catch_bad_credentials_error()

    def test_registration_different_passwords(self, test_data):
        app.register_page.open()
        app.register_page.registration(**test_data['user_data'][0], submit_password=f"{test_data['user_data'][0]['password']}_1")
        app.register_page.catch_different_passwords_error()
