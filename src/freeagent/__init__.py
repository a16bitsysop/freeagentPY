"""
Public class
"""

try:
    from ._version import version as __version__
except ModuleNotFoundError:
    # _version.py is written when building dist
    __version__ = "0.0.0+local"

from .base import DEFAULT_API_BASE_URL, FreeAgentBase
from .bank import BankAPI
from .bank_account import BankAccountAPI
from .category import CategoryAPI
from .transaction import TransactionAPI
from .payload import ExplanationPayload, UpdatePayload


class FreeAgent(FreeAgentBase):
    """
    The main public class
    """

    def __init__(self, api_base_url: str = DEFAULT_API_BASE_URL):
        """
        Create the client

        :param api_base_url: the url to use for requests, defaults to normal but can be
            changed to sandbox
        """
        super().__init__(api_base_url=api_base_url)  # initialise base class
        self.bank_account = BankAccountAPI(self)
        self.bank = BankAPI(self)
        self.category = CategoryAPI(self)
        self.transaction = TransactionAPI(self)
