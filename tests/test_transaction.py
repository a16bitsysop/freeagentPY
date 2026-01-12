"""
Unit tests for the TransactionAPI class using offline dummy data and mocks.
"""

# pylint: disable=protected-access, too-few-public-methods
import unittest
from unittest.mock import MagicMock

from freeagent.transaction import TransactionAPI


class TransactionAPITestCase(unittest.TestCase):
    """
    Unit tests for the TransactionAPI class using MagicMock and dummy data.
    """

    def setUp(self):
        # Set up a mock parent with get_api
        self.parent = MagicMock()
        self.api = TransactionAPI(self.parent)

    def test_get_transactions_success(self):
        """Test that transactions are fetched correctly for a valid category."""
        nominal_code = "123"
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        expected_transactions = {"transactions": ["transaction1", "transaction2"]}
        self.parent.get_api.return_value = expected_transactions

        transactions = self.api.get_transactions(nominal_code, start_date, end_date)

        self.parent.get_api.assert_called_once_with(
            "accounting/transactions",
            {
                "nominal_code": nominal_code,
                "from_date": start_date,
                "to_date": end_date,
            },
        )
        self.assertEqual(transactions, expected_transactions)


if __name__ == "__main__":
    unittest.main()
