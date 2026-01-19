"""
ExplanationPayload dataclass used by this module
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional, Dict


@dataclass
class ExplanationPayload:
    """
    dataclass used to store data for functions
    """

    nominal_code: str  # Required
    dated_on: date  # Required
    gross_value: Decimal  # Required
    description: Optional[str] = None  # Optional
    bank_transaction: Optional[str] = None  # Required for new explanations
    attachment: Optional[Dict] = None
    transfer_bank_account: Optional[str] = None
