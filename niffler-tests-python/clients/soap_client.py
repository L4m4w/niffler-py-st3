import requests
from models.config import Envs
from utils.sessions import SoapSession


class SoapClient:

    session: requests.Session
    base_url: str

    def __init__(self, base_url):
        self.session = SoapSession(base_url=base_url)
        self.session.headers.update(
            {
                'Content-Type': 'application/soap+xml'
            }
        )