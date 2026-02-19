"""
Public class
"""

try:
    from ._version import version as __version__
except ModuleNotFoundError:
    # _version.py is written when building dist
    __version__ = "0.0.0+local"

from .base import FreeAgentBase
from .bank import BankAPI
from .bank_account import BankAccountAPI
from .category import CategoryAPI
from .transaction import TransactionAPI
from .payload import ExplanationPayload, UpdatePayload


class FreeAgent(FreeAgentBase):
    """
    The main public class
    """

    def __init__(self):
        super().__init__()  # initialse base class
        self.bank_account = BankAccountAPI(self)
        self.bank = BankAPI(self)
        self.category = CategoryAPI(self)
        self.transaction = TransactionAPI(self)
