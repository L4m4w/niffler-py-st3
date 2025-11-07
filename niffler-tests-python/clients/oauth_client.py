import base64

import pkce

from models.config import Envs
from models.oauth import OAuthRequest
from utils.sessions import AuthSession


class OAuthClient:
    """Авторизация по OAuth2.0"""

    session: AuthSession
    base_url: str

    def __init__(self, env: Envs):
        self.session = AuthSession(base_url=env.auth_url)
        self.redirect_url = env.frontend_url + '/authorize'

        # self.code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
        # self.code_verifier = re.sub('[^a-zA-Z0-9]+', '', self.code_verifier)
        #
        # self.code_challenge = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        # self.code_challenge = base64.urlsafe_b64encode(self.code_challenge).decode('utf-8')
        # self.code_challenge = self.code_challenge.replace('=', '')
        self.code_verifier, self.code_challenge = pkce.generate_pkce_pair()

        self._basic_token = base64.b64encode(env.auth_secret.encode('utf-8')).decode('utf-8')
        self.authorization_basic = {"Authorization": f"Basic {self._basic_token}"}
        self.token = None

    def get_token(self, username, password):
        """Return oauth token to authorize user with username and password
        1. Get jsessionid and xsrf-token cookies in session.
        2. Get code frm redirect by xsrf-token
        3. Get access token
        """
        self.session.get(
            url="/oauth2/authorize",
            params=OAuthRequest(
                redirect_uri=self.redirect_url,
                code_challenge=self.session.code
            ).model_dump(),
            allow_redirects=True
        )

        self.session.post(
            url="/login",
            data={
                "username": username,
                "password": password,
                "_csrf": self.session.cookies.get("XSRF-TOKEN")
            },
            allow_redirects=True
        )

        token_response = self.session.post(
            url="/oauth2/token",
            data={
                "code": self.session.code,
                "redirect_uri": self.redirect_url,
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "client_id": "client"
            },
            headers=self.authorization_basic,
        )

        self.token = token_response.json().get("access_token", None)
        return self.token