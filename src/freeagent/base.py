"""
Base class the other class inherit from
"""

import json

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from getpass import getpass
from webbrowser import open as open_browser

from keyring import get_password, set_password
from requests_oauthlib import OAuth2Session


class FreeAgentBase:
    """
    Common functions used in other classes
    """

    SERVICE_NAME = "freeagent_token"
    TOKEN_KEY = "oauth2_token"

    def __init__(self, api_base_url: str = "https://api.freeagent.com/v2/"):
        """
        Initialize the base class

        :param api_base_url: the url to use for requests, defaults to normal but
            can be changed to sandbox
        """
        self.api_base_url = api_base_url
        self.session = None

    def get_credential(self, service: str, account: str, prompt_text: str) -> str:
        """
        Get a credential from the keyring, prompting to enter if needed

        :param service: service name of credential
        :param account: account name of credential
        :param promt_text: text to display when prompting for credential if not saved

        :return: the credential
        """
        cred = get_password(service, account)
        if cred is None:
            cred = getpass(f"{prompt_text}: ")
            set_password(service, account, cred)
            print(f"Stored {account} in keychain.")
        return cred

    def _save_token(self, token: str):
        """
        Save the oauth token to the keyring

        :param token: the token to save
        """
        set_password(self.SERVICE_NAME, self.TOKEN_KEY, json.dumps(token))

    def _load_token(self):
        """
        Load the oauth token from the keyring

        :return: token, or None if not found or error
        """
        token_json = get_password(self.SERVICE_NAME, self.TOKEN_KEY)
        try:
            return json.loads(token_json) if token_json else None
        except json.JSONDecodeError:
            print("⚠️ Invalid token in keyring. Re-auth required.")
            return None

    def authenticate(self):
        """
        Authenticate with the freeagent API
        """
        token_url = self.api_base_url + "token_endpoint"
        redirect_uri = "https://localhost/"

        client_id = self.get_credential(
            "freeagent_api",
            "freeagent_client_id",
            "Enter your FreeAgent OAuth identifier",
        )
        client_secret = self.get_credential(
            "freeagent_api",
            "freeagent_client_secret",
            "Enter your FreeAgent OAuth secret",
        )

        token = self._load_token()
        extra = {"client_id": client_id, "client_secret": client_secret}

        if token:
            oauth = OAuth2Session(
                client_id,
                token=token,
                auto_refresh_url=token_url,
                auto_refresh_kwargs=extra,
                token_updater=self._save_token,
            )
        else:
            oauth = OAuth2Session(
                client_id, redirect_uri=redirect_uri, scope=[self.api_base_url]
            )
            auth_url, _state = oauth.authorization_url(
                self.api_base_url + "approve_app"
            )
            print("🔐 Open this URL and authorise the app:", auth_url)
            open_browser(auth_url)
            redirect_response = input("📋 Paste the full redirect URL here: ").strip()

            token = oauth.fetch_token(
                token_url,
                authorization_response=redirect_response,
                client_secret=client_secret,
            )
            self._save_token(token)

        self.session = oauth
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def serialize_for_api(self, obj) -> dict[str, any]:
        """
        Convert dataclasses or dicts with Decimal, date, etc. into plain API-compatible dicts.

        :param obj: dataclass or dict to convert

        return: API-compatible dict
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

    def get_api(self, endpoint: str) -> dict[str, any]:
        """
        Perform an API get request

        :param endpoint: end part of the endpoint URL

        :return: response as a dict
        """
        response = self.session.get(self.api_base_url + endpoint)
        response.raise_for_status()
        return response.json()

    def put_api(self, url: str, root: str, updates: str):
        """
        Perform an API put request

        :param url: complete url for put request
        :param root: first part of payload
        :param updates: second part of payload

        :raises RunTimeError: if put request fails
        """
        payload = {root: updates}
        response = self.session.put(url, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"PUT failed {response.status_code}: {response.text}")

    def post_api(self, endpoint: str, root: str, payload: str):
        """
        Perform an API post request

        :param endpoint: end part of url endpoint
        :param root: first part of payload
        :param payload: second part of payload

        :raises RunTimeError: if post request fails
        """
        data = {root: payload}
        response = self.session.post(self.api_base_url + endpoint, json=data)
        if response.status_code not in (200, 201):
            raise RuntimeError(f"POST failed {response.status_code}: {response.text}")
        return response.json()
