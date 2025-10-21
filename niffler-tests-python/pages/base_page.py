import allure
from selene import have
from selene.support.shared import browser
from abc import ABC, abstractmethod


class BasePage(ABC):
    home_page=''

    def __init__(self):
        ...

    def open(self):
        with allure.step("Open page: " + self.PAGE_URL):
            browser.open(self.PAGE_URL)
            return self