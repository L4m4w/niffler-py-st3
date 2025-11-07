import os
import shutil

import allure
from allure_commons.types import Severity
from selene.support.shared import browser
import pytest

from models.user import UserData
# from utils.utils_pages.utils_account import login_ui
from pages.application import app

@allure.epic("niffler-auth")
@allure.feature("Authentication validation")
class TestAuthApp:

    @allure.story("Authorization")
    def test_successful_login(self, register_user):
        username, password = register_user
        app.login_page.open()
        app.login_page.login(username, password)
        assert app.login_page.check_login_status()

    @allure.story("Registration")
    def test_successful_registration(self, random_user: UserData):
        app.register_page.open()
        app.register_page.registration(random_user.username, random_user.password)
        assert app.register_page.check_registration_status()

    @allure.story("Authorization")
    def test_login_invalid_password_error(self, random_user: UserData):
        app.login_page.open()
        app.login_page.login(random_user.username, random_user.password)
        app.login_page.catch_bad_credentials_error()

    @allure.story("Registration")
    def test_registration_different_passwords(self, random_user: UserData):
        app.register_page.open()
        app.register_page.registration(random_user.username, random_user.password, submit_password=f"{random_user.password}_1")
        app.register_page.catch_different_passwords_error()

from marks import Pages, TestData

@allure.epic("niffler-auth")
@allure.feature("Authentication validation")
class TestAuthAppViaFixtures:

    @allure.story("Authorization")
    @Pages.auth_page
    def test_successful_login(self):
        assert app.login_page.check_login_status()

    @allure.story("Registration")
    @Pages.registration_page
    def test_successful_registration(self):
        assert app.register_page.check_registration_status()

    @allure.story("Authorization")
    @Pages.auth_page_with_wrong_password
    def test_login_invalid_password_error(self):
        app.login_page.catch_bad_credentials_error()

    @allure.story("Registration")
    @Pages.registration_page_with_different_passwords
    def test_registration_different_passwords(self):
        app.register_page.catch_different_passwords_error()

