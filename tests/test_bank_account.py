"""
Unit tests for the BankAccountAPI class.
"""

# pylint: disable=protected-access
import unittest
from unittest.mock import MagicMock
from freeagent.bank_account import BankAccountAPI


class BankAccountAPITestCase(unittest.TestCase):
    """
    Unit tests for the BankAccountAPI class.
    """

    def setUp(self):
        self.parent = MagicMock()
        self.api = BankAccountAPI(self.parent)

    def test_get_id_by_name(self):
        """Test finding a bank account ID by name."""
        acct1 = MagicMock()
        acct1.configure_mock(
            name="Standard", url="http://x/1", type="StandardBankAccount"
        )
        acct2 = MagicMock()
        acct2.configure_mock(name="PayPal", url="http://x/2", type="PaypalAccount")
        self.api.bank_accounts = [acct1, acct2]

        # Case insensitive match
        self.assertEqual(self.api.get_id_by_name("standard"), "1")
        self.assertEqual(self.api.get_id_by_name("PAYPAL"), "2")

        # Filter by type
        self.assertEqual(
            self.api.get_id_by_name("standard", "StandardBankAccount"), "1"
        )
        self.assertIsNone(self.api.get_id_by_name("standard", "PaypalAccount"))

        # Not found
        self.assertIsNone(self.api.get_id_by_name("NonExistent"))

    def test_get_name_by_id(self):
        """Test finding a bank account name by ID."""
        acct1 = MagicMock()
        acct1.configure_mock(name="Standard", url="http://x/1")
        self.api.bank_accounts = [acct1]

        self.assertEqual(self.api.get_name_by_id("1"), "Standard")
        self.assertEqual(self.api.get_name_by_id(1), "Standard")

        with self.assertRaises(ValueError):
            self.api.get_name_by_id("999")

    def test_get_name_by_uri(self):
        """Test finding a bank account name by URI."""
        acct1 = MagicMock()
        acct1.configure_mock(name="Standard", url="http://x/1")
        self.api.bank_accounts = [acct1]

        self.assertEqual(self.api.get_name_by_uri("http://x/1"), "Standard")

        with self.assertRaises(ValueError):
            self.api.get_name_by_uri("http://x/999")

    def test_get_first_id_by_type(self):
        """Test finding the first account ID of a certain type."""
        acct1 = MagicMock()
        acct1.configure_mock(url="http://x/1", type="StandardBankAccount")
        acct2 = MagicMock()
        acct2.configure_mock(url="http://x/2", type="PaypalAccount")
        self.api.bank_accounts = [acct1, acct2]

        self.assertEqual(self.api.get_first_id_by_type("PaypalAccount"), "2")
        self.assertIsNone(self.api.get_first_id_by_type("CreditCardAccount"))

    def test_get_primary_id(self):
        """Test finding the primary bank account ID."""
        acct1 = MagicMock()
        acct1.configure_mock(url="http://x/1", is_primary=False)
        acct2 = MagicMock()
        acct2.configure_mock(url="http://x/2", is_primary=True)
        self.api.bank_accounts = [acct1, acct2]

        self.assertEqual(self.api.get_primary_id(), "2")

    def test_get_primary_url(self):
        """Test finding the primary bank account URL."""
        acct1 = MagicMock()
        acct1.configure_mock(url="http://x/1", is_primary=False)
        acct2 = MagicMock()
        acct2.configure_mock(url="http://x/2", is_primary=True)
        self.api.bank_accounts = [acct1, acct2]

        self.assertEqual(self.api.get_primary_url(), "http://x/2")

    def test_get_paypal_id(self):
        """Test finding PayPal account ID by name."""
        acct = MagicMock()
        acct.configure_mock(name="PayPal", url="http://x/2", type="PaypalAccount")
        self.api.bank_accounts = [acct]
        self.assertEqual(self.api.get_paypal_id("PayPal"), "2")

    def test_get_first_paypal_id(self):
        """Test retrieval of the first PayPal account ID."""
        acct = MagicMock()
        acct.configure_mock(name="PayPal", url="http://x/2", type="PaypalAccount")
        self.api.bank_accounts = [acct]
        self.assertEqual(self.api.get_first_paypal_id(), "2")

    def test_get_id(self):
        """Test standard account ID lookup by name."""
        acct = MagicMock()
        acct.configure_mock(name="Main", url="http://x/3", type="StandardBankAccount")
        self.api.bank_accounts = [acct]
        self.assertEqual(self.api.get_id("Main"), "3")


if __name__ == "__main__":
    unittest.main()
