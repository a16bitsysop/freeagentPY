"""
Base class the other class inherit from
"""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from webbrowser import open as open_browser

from requests_oauthlib import OAuth2Session

from .utils import make_dataclass_from_dict


class FreeAgentBase:
    """
    Common functions used in other classes
    """

    def __init__(
        self,
        api_base_url: str = "https://api.freeagent.com/v2/",
    ):
        """
        Initialize the base class

        :param api_base_url: the url to use for requests, defaults to normal but can be
            changed to sandbox
        """
        self.api_base_url = api_base_url
        self.session = None

    def authenticate(
        self, oauth_ident: str, oauth_secret: str, save_token_cb, token: str = None
    ):
        """
        Authenticate with the freeagent API

        :param oauth_ident: oauth identifier from the freeagent dev dashboard
        :param oauth_secret: oauth secret from the freeagent dev dashboard
        :param save_token_cb: function to call when the token is refreshed to save it
        :param token: initial token, or None
        """
        token_url = self.api_base_url + "token_endpoint"
        redirect_uri = "https://localhost/"

        extra = {"client_id": oauth_ident, "client_secret": oauth_secret}

        if token:
            oauth = OAuth2Session(
                oauth_ident,
                token=token,
                auto_refresh_url=token_url,
                auto_refresh_kwargs=extra,
                token_updater=save_token_cb,
            )
        elif oauth_secret:
            oauth = OAuth2Session(
                oauth_ident, redirect_uri=redirect_uri, scope=[self.api_base_url]
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
                client_secret=oauth_secret,
            )
            save_token_cb(token)
        else:
            raise ValueError("Need oauth_secret, or oauth_token")

        self.session = oauth
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        # Get user info and print it
        user_info = self.get_api("users/me")
        first_name = user_info[0].user["first_name"]
        last_name = user_info[0].user["last_name"]
        print(f"✅ Authenticated! User info: {first_name} {last_name}")
        print()

    def serialize_for_api(self, obj) -> dict[str, any]:
        """
        Convert dataclasses or dicts with Decimal, date, etc. into plain API-compatible dicts

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

    def get_api(self, endpoint: str, params: dict = None) -> list:
        """
        Perform an API get request, handling pagination

        :param endpoint: end part of the endpoint URL
        :param params: dict of "Name": Value entries for request to process into URL

        :return: A list of dataclass instances
        """
        if params is None:
            params = {}

        per_page = 100
        params["per_page"] = per_page
        params["page"] = 1

        response = self.session.get(self.api_base_url + endpoint, params=params)
        response.raise_for_status()
        json_data = response.json()

        key = endpoint.split("/")[-1]
        class_name = key.rstrip("s")

        if not isinstance(json_data, dict) or key not in json_data:
            return [make_dataclass_from_dict(class_name, json_data)]

        items = [
            make_dataclass_from_dict(class_name, item)
            for item in json_data.get(key, [])
        ]

        if len(items) == per_page:
            page = 2
            while True:
                params["page"] = page
                response = self.session.get(self.api_base_url + endpoint, params=params)
                response.raise_for_status()
                json_data = response.json()

                if key in json_data:
                    current_items = json_data[key]
                    items.extend(
                        [
                            make_dataclass_from_dict(class_name, item)
                            for item in current_items
                        ]
                    )

                    if len(current_items) < per_page:
                        break
                else:
                    break

                page += 1

        return items

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
