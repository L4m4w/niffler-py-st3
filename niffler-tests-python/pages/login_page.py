import time

from selene import by, be
from selene.support.conditions import have
from selene.support.shared import browser

from pages.base_page import BasePage

from selenium.webdriver.remote.webelement import WebElement



class LoginPage(BasePage):

    PAGE_URL = 'http://frontend.niffler.dc/login'


    def login(self, email, password):
        browser.element("[name=username]").type(email)
        browser.element("[name=password]").type(password)
        browser.element('button.form__submit').click()
        return self

    @property
    def login_button(self) -> WebElement:
        return browser.element('button.form__submit').click()

    @property
    def registration_redirect_button(self):
        return browser.element(by.text('Create new account'))

    def enter_email(self, username):
        browser.element("[name=username]").type(username)
        return self

    def enter_password(self, password):
        browser.element("[name=password]").type(password)
        return self

    def catch_bad_credentials_error(self):
        return browser.element('p.form__error').should(have.text('Bad credentials'))

    def check_login_status(self):
        try:
            status = browser.element(by.id("spendings")).should(be.visible)
        except Exception as e:
            status = None
            print(e)
        return True if status else False
