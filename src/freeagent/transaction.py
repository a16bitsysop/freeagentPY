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

        :param api_base_url: the url to use for requests, defaults to normal but
            can be changed to sandbox
        """
        self.parent = parent  # the main FreeAgent instance

    def get_transactions(
        self, nominal_code: str, start_date: str, end_date: str
    ) -> list:
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

        return self.parent.get_api("accounting/transactions", params)
