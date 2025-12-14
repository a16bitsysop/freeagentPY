from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional, Dict

@dataclass
class ExplanationPayload:
    category: str  # Required
    dated_on: date  # Required
    gross_value: Decimal  # Required
    description: Optional[str] = None  # Optional
    bank_transaction: Optional[str] = None  # Required for new explanations
    attachment: Optional[Dict] = None