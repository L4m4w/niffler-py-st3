from urllib.parse import urljoin

import requests

from models.spend import Category, Spend


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

    def get_categories(self) -> list[Category]:
        response = self.session.get(urljoin(self.base_url, '/api/categories/all'))
        response.raise_for_status()

        return [Category.model_validate(item) for item in response.json()]

    def add_category(self, name: str) -> Category:
        response = self.session.post(urljoin(self.base_url, '/api/categories/add'), json={
            'name': name
        })
        response.raise_for_status()

        return Category.model_validate(response.json())

    def get_spends(self) -> list[Spend]:
        url = urljoin(self.base_url, '/api/spends/all')
        response = self.session.get(url)
        response.raise_for_status()
        return [Spend.model_validate(item) for item in response.json()]

    def add_spends(self, spend: Spend) -> Spend:
        url = urljoin(self.base_url, '/api/spends/add')
        response = self.session.post(url, json = spend.model_dump())
        papap = spend.model_dump()
        response.raise_for_status()
        return Spend.model_validate(response.json())

    def remove_spends(self, ids: list[str]):
        url = urljoin(self.base_url, '/api/spends/remove')
        response = self.session.delete(url, params={'ids': ids})
        response.raise_for_status()