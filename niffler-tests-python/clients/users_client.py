from urllib.parse import urljoin

import allure
import requests
from allure_commons.types import AttachmentType
from requests import Response
from requests_toolbelt.utils.dump import dump_response

from models.userdata import UserUpdateProfile


class UsersHttpClient:

    session: requests.Session
    base_url: str

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.session()
        self.session.headers.update(
            {
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        self.session.hooks['response'].append(self.attach_response)

    @staticmethod
    def attach_response(response: Response, *args, **kwargs):
        attachment_name = response.request.method + " " + response.request.url
        allure.attach(dump_response(response), attachment_name, attachment_type=AttachmentType.TEXT)

    @allure.step('Getting current User profile via http request: /api/users/current')
    def get_current_user(self):
        response = self.session.get(urljoin(self.base_url, '/api/users/current'))
        response.raise_for_status()

        return response.json()

    @allure.step('Getting all user profiles via http request: /api/users/all')
    def get_all_users(self):
        response = self.session.get(urljoin(self.base_url, '/api/users/all'))
        response.raise_for_status()

        return response.json()

    @allure.step('Updating User profile via http request: /api/users/update')
    def update_user(self, body) -> UserUpdateProfile:
        url = urljoin(self.base_url, '/api/users/update')
        response = self.session.post(url, json=body)

        response.raise_for_status()
        return UserUpdateProfile.model_validate(response.json())


