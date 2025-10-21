import time

from selene import by, be
from selene.support.conditions import have
from selene.support.shared import browser

from pages.base_page import BasePage

from selenium.webdriver.remote.webelement import WebElement



class RegistrationPage(BasePage):

    PAGE_URL = 'http://auth.niffler.dc:9000/register'


    def registration(self, username, password, submit_password = None):
        browser.element("[name=username]").type(username)
        browser.element("[name=password]").type(password)
        browser.element("[name=passwordSubmit]").type(submit_password or password)
        browser.element('button.form__submit').click()
        return self

    @property
    def register_button(self) -> WebElement:
        return browser.element('button.form__submit').click()

    def enter_username(self, username):
        browser.element("[name=username]").type(username)
        return self

    def enter_password(self, password):
        browser.element("[name=password]").type(password)
        return self

    def enter_submit_password(self, password):
        browser.element("[name=passwordSubmit]").type(password)
        return self

    def catch_different_passwords_error(self):
        try:
            status = browser.element('span.form__error').should(have.text('Passwords should be equal'))
        except Exception as e:
            status = None
            print(e)
        return True if status else False

    def check_registration_status(self):
        try:
            # <p class="form__paragraph">Congratulations! You've registered!</p>
            status = browser.element(by.class_name('form__paragraph_success')).should(have.text("Congratulations! You've registered!"))
        except Exception as e:
            status = None
            print(e)
        return True if status else False
