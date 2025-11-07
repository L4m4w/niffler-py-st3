from urllib.parse import urljoin

import allure
import requests
from allure_commons.types import AttachmentType
from requests import Response
from requests_toolbelt.utils.dump import dump_response

from models.config import Envs
from models.userdata import UserUpdateProfile
from utils.sessions import BaseSession


class UsersHttpClient:

    session: requests.Session
    base_url: str

    def __init__(self, env: Envs, token: str):
        self.session = BaseSession(base_url=env.gateway_url)
        self.session.headers.update(
            {
                'Accept': 'application/json',
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
    #
    # @staticmethod
    # def attach_response(response: Response, *args, **kwargs):
    #     attachment_name = response.request.method + " " + response.request.url
    #     allure.attach(dump_response(response), attachment_name, attachment_type=AttachmentType.TEXT)

    @allure.step('Getting current User profile via http request: /api/users/current')
    def get_current_user(self):
        response = self.session.get('/api/users/current')

        return response.json()

    @allure.step('Getting all user profiles via http request: /api/users/all')
    def get_all_users(self):
        response = self.session.get('/api/users/all')

        return response.json()

    @allure.step('Updating User profile via http request: /api/users/update')
    def update_user(self, body) -> UserUpdateProfile:
        response = self.session.post('/api/users/update', json=body)

        return UserUpdateProfile.model_validate(response.json())


