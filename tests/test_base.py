"""
Unit tests for the FreeAgentBase class using offline dummy data and mocks.
Covers serialization, API get/put/post calls, pagination, and OAuth flow.
"""

# pylint: disable=protected-access, too-few-public-methods
import unittest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from freeagent.base import FreeAgentBase
from freeagent.payload import ExplanationPayload


class FreeAgentBaseTestCase(unittest.TestCase):
    """
    Unit tests for the FreeAgentBase class using MagicMock and dummy data.
    """

    def setUp(self):
        self.api = FreeAgentBase()

    def test_serialize_for_api(self):
        """Test that Decimal, date, datetime and nested values are converted."""
        obj = {
            "amount": Decimal("1.50"),
            "dated_on": date(2023, 1, 1),
            "created_at": datetime(2023, 1, 1, 12, 30, 0),
            "nested": {"rate": Decimal("2.0")},
            "items": [Decimal("1.00"), date(2023, 2, 2)],
            "skip": None,
        }
        result = self.api.serialize_for_api(obj)
        self.assertEqual(
            result,
            {
                "amount": "1.50",
                "dated_on": "2023-01-01",
                "created_at": "2023-01-01T12:30:00",
                "nested": {"rate": "2.0"},
                "items": ["1.00", "2023-02-02"],
            },
        )
        self.assertNotIn("skip", result)

    def test_serialize_for_api_dataclass(self):
        """Test that dataclass instances are serialized like dicts."""
        payload = ExplanationPayload(
            nominal_code="250",
            dated_on=date(2023, 1, 1),
            gross_value=Decimal("10.99"),
            description="Inc",
        )
        result = self.api.serialize_for_api(payload)
        self.assertEqual(result["gross_value"], "10.99")
        self.assertEqual(result["dated_on"], "2023-01-01")
        self.assertEqual(result["description"], "Inc")
        self.assertNotIn("attachment", result)

    def test_get_api_single_page(self):
        """Test a single-page response with no further pagination."""
        response = MagicMock()
        response.json.return_value = {"bank_transactions": [{"id": 1}, {"id": 2}]}
        self.api.session = MagicMock()
        self.api.session.get.return_value = response

        items = self.api.get_api("bank_transactions")

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].id, 1)
        self.api.session.get.assert_called_once_with(
            "https://api.freeagent.com/v2/bank_transactions",
            params={"page": 1, "per_page": 100},
        )

    def test_get_api_pagination(self):
        """Test that a full page of 100 triggers fetching the next page."""
        page1 = MagicMock()
        page1.json.return_value = {"bank_transactions": [{"id": i} for i in range(100)]}
        page2 = MagicMock()
        page2.json.return_value = {"bank_transactions": [{"id": 100}]}
        self.api.session = MagicMock()
        self.api.session.get.side_effect = [page1, page2]

        items = self.api.get_api("bank_transactions")

        self.assertEqual(len(items), 101)
        self.assertEqual(items[-1].id, 100)
        self.assertEqual(self.api.session.get.call_count, 2)
        self.assertEqual(
            self.api.session.get.call_args_list[1].kwargs["params"]["page"], 2
        )

    def test_get_api_stops_when_key_missing(self):
        """Test that pagination stops when a later page omits the key."""
        page1 = MagicMock()
        page1.json.return_value = {"bank_transactions": [{"id": i} for i in range(100)]}
        page2 = MagicMock()
        page2.json.return_value = {"errors": ["rate limited"]}
        self.api.session = MagicMock()
        self.api.session.get.side_effect = [page1, page2]

        items = self.api.get_api("bank_transactions")

        self.assertEqual(len(items), 100)
        self.assertEqual(self.api.session.get.call_count, 2)

    def test_get_api_non_list_response(self):
        """Test an object-shaped response (e.g. users/me) still works."""
        response = MagicMock()
        response.json.return_value = {"user": {"first_name": "Ada", "last_name": "L"}}
        self.api.session = MagicMock()
        self.api.session.get.return_value = response

        items = self.api.get_api("users/me")

        self.assertEqual(items[0].user["first_name"], "Ada")

    def test_get_api_does_not_mutate_params(self):
        """Test that the caller's params dict is not modified."""
        response = MagicMock()
        response.json.return_value = {"bank_transactions": []}
        self.api.session = MagicMock()
        self.api.session.get.return_value = response

        params = {"bank_account": "x"}
        self.api.get_api("bank_transactions", params)

        self.assertEqual(params, {"bank_account": "x"})

    def test_put_api_success(self):
        """Test a successful PUT request."""
        self.api.session = MagicMock()
        self.api.session.put.return_value = MagicMock(status_code=200)

        self.api.put_api("http://x", "root", {"a": 1})

        self.api.session.put.assert_called_once_with(
            "http://x", json={"root": {"a": 1}}
        )

    def test_put_api_failure(self):
        """Test a failed PUT raises RuntimeError."""
        self.api.session = MagicMock()
        self.api.session.put.return_value = MagicMock(status_code=400, text="bad")

        with self.assertRaises(RuntimeError):
            self.api.put_api("http://x", "root", {"a": 1})

    def test_post_api_success(self):
        """Test a successful POST request."""
        response = MagicMock(status_code=201)
        response.json.return_value = {"ok": True}
        self.api.session = MagicMock()
        self.api.session.post.return_value = response

        result = self.api.post_api("bank_transactions", "bank_transaction", {"a": 1})

        self.assertEqual(result, {"ok": True})
        self.api.session.post.assert_called_once_with(
            "https://api.freeagent.com/v2/bank_transactions",
            json={"bank_transaction": {"a": 1}},
        )

    def test_post_api_failure(self):
        """Test a failed POST raises RuntimeError."""
        self.api.session = MagicMock()
        self.api.session.post.return_value = MagicMock(status_code=500, text="boom")

        with self.assertRaises(RuntimeError):
            self.api.post_api("bank_transactions", "bank_transaction", {})

    @patch("freeagent.base.OAuth2Session.get")
    def test_authenticate_with_existing_token(self, mock_get):
        """Test authenticate with a stored token uses no browser flow."""
        response = MagicMock()
        response.json.return_value = {
            "user": {"first_name": "Ada", "last_name": "Lovelace"}
        }
        mock_get.return_value = response

        token = {"access_token": "abc", "refresh_token": "def"}
        save_cb = MagicMock()
        with patch("builtins.print"):
            self.api.authenticate("ident", "secret", save_cb, token)

        self.assertIsNotNone(self.api.session)
        self.assertEqual(self.api.session.headers["Accept"], "application/json")
        save_cb.assert_not_called()

    def test_authenticate_loopback(self):
        """Test the interactive loopback callback flow."""
        user = MagicMock(user={"first_name": "Ada", "last_name": "Lovelace"})
        save_cb = MagicMock()
        with (
            patch("builtins.print"),
            patch("freeagent.base.open_browser"),
            patch(
                "freeagent.base.receive_oauth_code", return_value="auth123"
            ) as mock_receive,
            patch(
                "freeagent.base.OAuth2Session.fetch_token",
                return_value={"access_token": "new"},
            ) as mock_fetch,
            patch.object(self.api, "get_api", return_value=[user]),
        ):
            self.api.authenticate("ident", "secret", save_cb)

        mock_receive.assert_called_once()
        mock_fetch.assert_called_once()
        save_cb.assert_called_once_with({"access_token": "new"})

    def test_authenticate_callback_timeout(self):
        """Test that a missing browser callback raises RuntimeError."""
        with (
            patch("builtins.print"),
            patch("freeagent.base.open_browser"),
            patch("freeagent.base.receive_oauth_code", return_value=None),
            patch.object(self.api, "get_api") as mock_get_api,
        ):
            with self.assertRaises(RuntimeError):
                self.api.authenticate("ident", "secret", MagicMock())
        mock_get_api.assert_not_called()

    def test_authenticate_no_credentials(self):
        """Test that missing oauth_secret and token raises ValueError."""
        with self.assertRaises(ValueError):
            self.api.authenticate("ident", None, MagicMock())


if __name__ == "__main__":
    unittest.main()
