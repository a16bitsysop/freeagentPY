"""
Class for getting freeagent transactions
"""

from datetime import datetime
from decimal import Decimal
from typing import List

from .base import FreeAgentBase
from .payload import Transaction


class TransactionAPI(FreeAgentBase):
    """
    The TransactionAPI class
    """

    def __init__(self, parent):  # pylint: disable=super-init-not-called
        """
        Initialize the class
        """
        self.parent = parent  # the main FreeAgent instance

    def get_transactions(
        self, nominal_code: str, start_date: str, end_date: str
    ) -> List[Transaction]:
        """
        Get transactions for a given category nominal code and date range.

        :param nominal_code: The nominal code of the category.
        :param start_date: Start date of the date range (YYYY-MM-DD).
        :param end_date: End date of the date range (YYYY-MM-DD).
        :return: A list of Transaction objects.
        """
        params = {
            "nominal_code": nominal_code,
            "from_date": start_date,
            "to_date": end_date,
        }

        response = self.parent.get_api("accounting/transactions", params)
        transactions = []
        for transaction_data in response.get("transactions", []):
            transaction = Transaction(
                url=transaction_data["url"],
                dated_on=datetime.strptime(
                    transaction_data["dated_on"], "%Y-%m-%d"
                ).date(),
                created_at=datetime.fromisoformat(transaction_data["created_at"]),
                updated_at=datetime.fromisoformat(transaction_data["updated_at"]),
                description=transaction_data["description"],
                category=transaction_data["category"],
                category_name=transaction_data["category_name"],
                nominal_code=transaction_data["nominal_code"],
                debit_value=Decimal(transaction_data["debit_value"]),
                source_item_url=transaction_data.get("source_item_url"),
                foreign_currency_data=transaction_data.get("foreign_currency_data"),
            )
            transactions.append(transaction)
        return transactions
