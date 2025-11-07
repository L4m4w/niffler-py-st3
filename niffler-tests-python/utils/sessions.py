from urllib.parse import urlparse, parse_qs

import requests
from requests import Session

from utils.allure_helpers import allure_attach_request

def raise_for_status(function):
    def wrapper(*args, **kwargs):
        response = function(*args, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code in (400, 401, 404, 409, 500):
                e.add_note(response.text)
                raise
        return response
    return wrapper



class BaseSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_url = kwargs.pop('base_url', '')

    @raise_for_status
    @allure_attach_request
    def request(self, method, url, **kwargs):
        """Logging request"""
        url = self.base_url + url
        response = super().request(method, url, **kwargs)
        return response


class AuthSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_url = kwargs.pop('base_url', '')
        self.code = None

    @raise_for_status
    @allure_attach_request
    def request(self, method, url, **kwargs):
        """
        Save cookies from redirect and code from auth
        :param method:
        :param url:
        :param kwargs:
        :return:
        """
        response = super().request(method, self.base_url + url, **kwargs)
        for r in response.history:
            cookies = r.cookies.get_dict()
            self.cookies.update(cookies)
            code = parse_qs(urlparse(r.headers.get("Location")).query).get("code", None)
            if code:
                self.code = code
        return response