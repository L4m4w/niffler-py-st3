from urllib.parse import urljoin

import requests



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

    def get_current_user(self):
        response = self.session.get(urljoin(self.base_url, '/api/users/current'))
        response.raise_for_status()

        return response.json()

    def get_all_users(self):
        response = self.session.get(urljoin(self.base_url, '/api/users/all'))
        response.raise_for_status()

        return response.json()

    def update_user(self, body):
        url = urljoin(self.base_url, '/api/users/update')
        response = self.session.post(url, json=body)

        response.raise_for_status()
        return response.json()


