from base64 import b64encode
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from .base import FreeAgentBase
from .payload import ExplanationPayload

def serialize_for_api(obj):
    """
    Convert a dataclass object into a FreeAgent API-compatible dict.
    Only accepts dataclasses.
    """
    if not is_dataclass(obj):
        raise TypeError("Expected a dataclass instance")

    obj_dict = asdict(obj)

    def convert(val):
        if isinstance(val, Decimal):
            return str(val)
        if isinstance(val, (date, datetime)):
            return val.isoformat()
        if isinstance(val, dict):
            return {k: convert(v) for k, v in val.items()}
        if isinstance(val, list):
            return [convert(i) for i in val]
        return val

    return {k: convert(v) for k, v in obj_dict.items() if v is not None}

class BankAPI(FreeAgentBase):
    def __init__(self, parent):
        self.parent = parent  # the main FreeAgent instance

    def _check_file_size(self, path: Path):
        MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024  # 5 MB
        size = path.stat().st_size
        if size > MAX_ATTACHMENT_SIZE:
            raise ValueError(f"Attachment too large ({size} bytes). Max allowed is 5 MB.")
        return size

    def _encode_file_base64(self, path: Path) -> str:
        self._check_file_size(path)
        with path.open("rb") as f:
            return b64encode(f.read()).decode("utf-8")

    def _get_filetype(self, filename: Path) -> str:
        ALLOWED_TYPES = {
            ".pdf": "application/x-pdf",
            ".png": "image/x-png",
            ".jpeg": "image/jpeg",
            ".jpg": "image/jpeg",
            ".gif": "image/gif",
        }
        # Guess FreeAgent content type
        content_type = ALLOWED_TYPES.get(filename.suffix.lower())
        if not content_type:
            raise ValueError(f"Unsupported file type for FreeAgent: {path.suffix}")

        return content_type

    def attach_file_to_explanation(self, payload: ExplanationPayload, path, description=None):
        # freeagent supports:
        # image/x-png image/jpeg image/jpg image/gif application/x-pdf
        file_data = self._encode_file_base64(path)
        file_type = self._get_filetype(path)

        payload.attachment = {
            "file_name": path.name,
            "description": description or "Attachment",
            "content_type": file_type,
            "data": file_data,
        }

    def explain_transaction(self, tx_obj, dryrun=False):
        json_data = serialize_for_api(tx_obj)
        print(json_data["description"], json_data.get("gross_value"))
        if not dryrun:
            self.parent.post_api(
                "bank_transaction_explanations", "bank_transaction_explanation", json_data
            )

    def explain_update(self, url, tx_obj, dryrun=False):
        json_data = serialize_for_api(tx_obj)
        print(json_data["description"], json_data.get("gross_value"))
        if not dryrun:
            self.parent.put_api(url, "bank_transaction_explanation", json_data)

    def get_unexplained_transactions(self, account_id):
        return self.parent.get_api(
            f"bank_transactions?bank_account={account_id}&view=unexplained"
        )

    def _find_bank_name(self, bank_accounts, account_name):
        for account in bank_accounts:
            if account["name"].lower() == account_name.lower():
                return account["url"].rsplit("/", 1)[-1]
        return None

    def get_paypalID(self, account_name):
        response = self.parent.get_api("bank_accounts?view=paypal_accounts")
        return self._find_bank_name(response.get("bank_accounts", []), account_name)

    def get_first_paypalID(self):
        response = self.parent.get_api("bank_accounts?view=paypal_accounts")
        accounts = response.get("bank_accounts", [])
        if accounts:
            return accounts[0]["url"].rsplit("/", 1)[-1]
        return None

    def get_ID(self, account_name):
        response = self.parent.get_api("bank_accounts?view=standard_bank_accounts")
        return self._find_bank_name(response.get("bank_accounts", []), account_name)

    def get_primary(self):
        response = self.parent.get_api("bank_accounts?view=standard_bank_accounts")
        for acct in response.get("bank_accounts", []):
            if acct.get("is_primary"):
                return acct["url"].rsplit("/", 1)[-1]
        return None
    