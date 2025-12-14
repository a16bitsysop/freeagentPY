import json

from getpass import getpass
from keyring import get_password, set_password
from requests_oauthlib import OAuth2Session
from webbrowser import open as open_browser


class FreeAgentBase:
    SERVICE_NAME = "freeagent_token"
    TOKEN_KEY = "oauth2_token"

    def __init__(self, api_base_url="https://api.freeagent.com/v2/"):
        self.API_BASE_URL = api_base_url
        self.session = None

    def get_credential(self, service, account, prompt_text):
        cred = get_password(service, account)
        if cred is None:
            cred = getpass(f"{prompt_text}: ")
            set_password(service, account, cred)
            print(f"Stored {account} in keychain.")
        return cred

    def _save_token(self, token):
        set_password(self.SERVICE_NAME, self.TOKEN_KEY, json.dumps(token))

    def _load_token(self):
        token_json = get_password(self.SERVICE_NAME, self.TOKEN_KEY)
        try:
            return json.loads(token_json) if token_json else None
        except json.JSONDecodeError:
            print("⚠️ Invalid token in keyring. Re-auth required.")
            return None

    def authenticate(self):
        TOKEN_URL = self.API_BASE_URL + "token_endpoint"
        REDIRECT_URI = "https://localhost/"

        CLIENT_ID = self.get_credential(
            "freeagent_api",
            "freeagent_client_id",
            "Enter your FreeAgent OAuth identifier",
        )
        CLIENT_SECRET = self.get_credential(
            "freeagent_api",
            "freeagent_client_secret",
            "Enter your FreeAgent OAuth secret",
        )

        token = self._load_token()
        extra = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}

        if token:
            oauth = OAuth2Session(
                CLIENT_ID,
                token=token,
                auto_refresh_url=TOKEN_URL,
                auto_refresh_kwargs=extra,
                token_updater=self._save_token,
            )
        else:
            oauth = OAuth2Session(
                CLIENT_ID, redirect_uri=REDIRECT_URI, scope=[self.API_BASE_URL]
            )
            auth_url, state = oauth.authorization_url(self.API_BASE_URL + "approve_app")
            print("🔐 Open this URL and authorise the app:", auth_url)
            open_browser(auth_url)
            redirect_response = input("📋 Paste the full redirect URL here: ").strip()

            token = oauth.fetch_token(
                TOKEN_URL,
                authorization_response=redirect_response,
                client_secret=CLIENT_SECRET,
            )
            self._save_token(token)

        self.session = oauth
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def serialize_for_api(obj):
        """
        Convert dataclasses or dicts with Decimal, date, etc. into plain API-compatible dicts.
        """
        if is_dataclass(obj):
            obj = asdict(obj)

        def convert(val):
            if isinstance(val, Decimal):
                return str(val)
            if isinstance(val, (date, datetime)):
                return val.isoformat()
            if isinstance(val, dict):
                return {k: convert(v) for k, v in val.items()}
            if isinstance(val, list):
                return [convert(i) for i in val]
            return val

        return {k: convert(v) for k, v in obj.items() if v is not None}

    def get_api(self, endpoint):
        response = self.session.get(self.API_BASE_URL + endpoint)
        response.raise_for_status()
        return response.json()

    def put_api(self, url, root, updates):
        payload = {root: updates}
        response = self.session.put(url, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"PUT failed {response.status_code}: {response.text}")

    def post_api(self, endpoint, root, payload):
        data = {root: payload}
        response = self.session.post(self.API_BASE_URL + endpoint, json=data)
        if response.status_code not in (200, 201):
            raise RuntimeError(f"POST failed {response.status_code}: {response.text}")
        return response.json()
