from selene.support.shared import browser
from pages.login_page import LoginPage
from pages.register_page import RegistrationPage


class Application:
    def __init__(self):
        self.login_page = LoginPage()
        self.register_page = RegistrationPage()

    # def open(self):
    #     browser.open('/')
    #     return self


app = Application()