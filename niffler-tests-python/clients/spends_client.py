from urllib.parse import urljoin

import allure
import requests
from allure_commons.types import AttachmentType
from requests_toolbelt.utils.dump import dump_response
from requests import Response

from models.spend import Category, SpendModel


class SpendsHttpClient:

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

    @allure.step('Getting categories via http request: /api/categories/all')
    def get_categories(self) -> list[Category]:
        response = self.session.get(urljoin(self.base_url, '/api/categories/all'))
        self.raise_for_status(response)

        return [Category.model_validate(item) for item in response.json()]

    @allure.step('Adding categories via http request: /api/categories/add')
    def add_category(self, name: str) -> Category:
        response = self.session.post(urljoin(self.base_url, '/api/categories/add'), json={
            'name': name
        })
        self.raise_for_status(response)

        return Category.model_validate(response.json())

    @allure.step('Getting spends via http request: /api/spends/all')
    def get_spends(self) -> list[SpendModel]:
        url = urljoin(self.base_url, '/api/spends/all')
        response = self.session.get(url)
        self.raise_for_status(response)
        return [SpendModel.model_validate(item) for item in response.json()]

    @allure.step('Adding spends via http request: /api/spends/add')
    def add_spends(self, spend: SpendModel) -> SpendModel:
        url = urljoin(self.base_url, '/api/spends/add')
        spend_data = {
            'amount': spend.amount,
            'description': spend.description,
            'spendDate': spend.spendDate,
            'currency': spend.currency,
            'category': {'name': spend.category.name}
        }
        response = self.session.post(url, json = spend_data)

        self.raise_for_status(response)
        return SpendModel.model_validate(response.json())

    @allure.step('Removing spends by id via http request: /api/spends/remove')
    def remove_spends(self, ids: list[str]):
        url = urljoin(self.base_url, '/api/spends/remove')
        response = self.session.delete(url, params={'ids': ids})
        self.raise_for_status(response)

    @staticmethod
    def raise_for_status(response: requests.Response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if requests.status_codes in (400, 401,404, 409, 500) :
                e.add_note(response.text)
                raise