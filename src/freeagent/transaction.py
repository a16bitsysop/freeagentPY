"""
Class for getting freeagent transactions
"""

from .base import FreeAgentBase


class TransactionAPI(FreeAgentBase):
    """
    The TransactionAPI class
    """

    def __init__(self, parent):  # pylint: disable=super-init-not-called
        """
        Initialize the class
        """
        self.parent = parent  # the main FreeAgent instance

    def get_transactions(self, category: str, start_date: str, end_date: str) -> dict:
        """
        Get transactions for a given category nominal code and date range.

        :param category: URI of the category.
        :param start_date: Start date of the date range (YYYY-MM-DD).
        :param end_date: End date of the date range (YYYY-MM-DD).
        :return: A dictionary containing the transactions.
        """
        params = {"category": category, "from_date": start_date, "to_date": end_date}

        return self.parent.get_api("transactions", params)
