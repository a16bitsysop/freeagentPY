"""
Public class
"""

__version__ = "0.1"
__doc__ = "Python module for accessing freeagent using the API"

from .base import FreeAgentBase
from .bank import BankAPI
from .category import CategoryAPI
from .payload import ExplanationPayload


class FreeAgent(FreeAgentBase):
    """
    The main public class
    """

    def __init__(self):
        super().__init__()  # initialse base class
        self.bank = BankAPI(self)
        self.category = CategoryAPI(self)
