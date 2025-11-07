from urllib.parse import urljoin

import allure
import requests
from allure_commons.types import AttachmentType
from requests_toolbelt.utils.dump import dump_response
from requests import Response

from models.config import Envs
from models.spend import SpendModel, Category
from utils.sessions import BaseSession


class SpendsHttpClient:

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
        # self.session.hooks['response'].append(self.attach_response)

    # @staticmethod
    # def attach_response(response: Response, *args, **kwargs):
    #     attachment_name = response.request.method + " " + response.request.url
    #     allure.attach(dump_response(response), attachment_name, attachment_type=AttachmentType.TEXT)

    @allure.step('Getting categories via http request: /api/categories/all')
    def get_categories(self) -> list[Category]:
        response = self.session.get('/api/categories/all')

        return [Category.model_validate(item) for item in response.json()]

    @allure.step('Adding categories via http request: /api/categories/add')
    def add_category(self, name: str) -> Category:
        response = self.session.post('/api/categories/add', json={
            'name': name
        })

        return Category.model_validate(response.json())

    @allure.step('Getting spends via http request: /api/spends/all')
    def get_spends(self) -> list[SpendModel]:
        response = self.session.get('/api/spends/all')
        return [SpendModel.model_validate(item) for item in response.json()]

    @allure.step('Adding spends via http request: /api/spends/add')
    def add_spends(self, spend: SpendModel) -> SpendModel:
        spend_data = {
            'amount': spend.amount,
            'description': spend.description,
            'spendDate': spend.spendDate,
            'currency': spend.currency,
            'category': {'name': spend.category.name}
        }
        response = self.session.post('/api/spends/add', json = spend_data)

        return SpendModel.model_validate(response.json())

    @allure.step('Removing spends by id via http request: /api/spends/remove')
    def remove_spends(self, ids: list[str]):
        self.session.delete('/api/spends/remove', params={'ids': ids})
