"""
ExplanationPayload dataclass used by this module
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, List


@dataclass
class Transaction:
    """
    dataclass for a single transaction
    """

    url: str
    dated_on: date
    created_at: datetime
    updated_at: datetime
    description: str
    category: str
    category_name: str
    nominal_code: str
    debit_value: Decimal
    source_item_url: Optional[str] = None
    foreign_currency_data: Optional[Dict] = None


@dataclass
class ExplanationPayload:
    """
    dataclass used to store data for functions
    """

    category: str  # Required
    dated_on: date  # Required
    gross_value: Decimal  # Required
    description: Optional[str] = None  # Optional
    bank_transaction: Optional[str] = None  # Required for new explanations
    attachment: Optional[Dict] = None
    transfer_bank_account: Optional[str] = None
