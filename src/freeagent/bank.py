"""
This module provides the BankAPI class to retreive information
about bank accounts on freeagent
"""

from base64 import b64encode
from pathlib import Path

from .base import FreeAgentBase
from .payload import ExplanationPayload


class BankAPI(FreeAgentBase):
    """
    BankAPI class to retreive information
    about bank accounts on freeagent

    Initialize the base class

    :param api_base_url: the url to use for requests, defaults to normal but
        can be changed to sandbox
    """

    def __init__(self, parent):  # pylint: disable=super-init-not-called
        """
        Initialize the BankAPI class
        """
        self.parent = parent  # the main FreeAgent instance

    def _check_file_size(self, path: Path) -> int:
        """
        Helper funtion to check file size for attaching files to explanations

        :param path: pathlike Path of the file to check

        :return: filesize in bytes
        :raises ValueError: if the filesize is larger than 5MB (freeagent limit)
        """
        max_attachment_size = 5 * 1024 * 1024  # 5 MB
        size = path.stat().st_size
        if size > max_attachment_size:
            raise ValueError(
                f"Attachment too large ({size} bytes). Max allowed is 5 MB."
            )
        return size

    def _encode_file_base64(self, path: Path) -> str:
        """
        Encode the passed file as base64 after checking size

        :param path: pathlike Path of the file to encode

        :return: string of the encoded file
        """
        self._check_file_size(path)
        with path.open("rb") as f:
            return b64encode(f.read()).decode("utf-8")

    def _get_filetype(self, filename: Path) -> str:
        """
        Guess the filetype based on dot extension of name

        :param filename: pathlike Path of the file to guess

        :return: string of the filetype
        :raises ValueError: if file is not a type supported by freeagent
        """
        allowed_types = {
            ".pdf": "application/x-pdf",
            ".png": "image/x-png",
            ".jpeg": "image/jpeg",
            ".jpg": "image/jpeg",
            ".gif": "image/gif",
        }
        # Guess FreeAgent content type
        content_type = allowed_types.get(filename.suffix.lower())
        if not content_type:
            raise ValueError(f"Unsupported file type for FreeAgent: {filename.suffix}")

        return content_type

    def attach_file_to_explanation(
        self, payload: ExplanationPayload, path: Path, description: str = None
    ):
        """
        Attach a file to an existing ExplanationPayload
        freeagent supports:

        - image/x-png
        - image/jpeg
        - image/jpg
        - image/gif
        - application/x-pdf

        :param payload: ExplanationPayload to add the file to
        :param description: optional description to use for the file on freeagent
        """
        file_data = self._encode_file_base64(path)
        file_type = self._get_filetype(path)

        payload.attachment = {
            "file_name": path.name,
            "description": description or "Attachment",
            "content_type": file_type,
            "data": file_data,
        }

    def explain_transaction(self, tx_obj: ExplanationPayload, dryrun: bool = False):
        """
        Post the explanation to freeagent in the passed ExplanationPayload tx_obj

        :param tx_obj: ExplanationPayload to use
        :param dry_run: if True then do not post to freeagent, only print details
        """
        json_data = self.serialize_for_api(tx_obj)

        print(json_data["description"], json_data.get("gross_value"))
        if not dryrun:
            self.parent.post_api(
                "bank_transaction_explanations",
                "bank_transaction_explanation",
                json_data,
            )

    def explain_update(
        self, url: str, tx_obj: ExplanationPayload, dryrun: bool = False
    ):
        """
        Update an existing explanation on freeagent with the passed url

        :param url: url attribute of the bank transaction explanation to change
        :param tx_obj: ExplanationPayload to use for updating the explanation
        :param dry_run: if True then do not post to freeagent, only print details
        """
        json_data = self.serialize_for_api(tx_obj)

        print(json_data["description"], json_data.get("gross_value"))
        if not dryrun:
            self.parent.put_api(url, "bank_transaction_explanation", json_data)

    def get_unexplained_transactions(self, account_id: str) -> list:
        """
        Return a list of unexplained transaction objects for the bank account with id of account_id

        :param account_id: account id to use, not the whole url

        :return: list of the unexplained transactions
        """
        params = {"bank_account": account_id, "view": "unexplained"}
        return self.parent.get_api("bank_transactions", params)

    def _find_bank_id(self, bank_accounts: list, account_name: str) -> str:
        """
        Get the freeagent bank account ID for account_name

        :param bank_accounts: a list of the bank accounts on freeagent
        :param account_name: name of the account to find

        :return: the id of the bank account or None if not found
        """
        for account in bank_accounts:
            if account.name.lower() == account_name.lower():
                return account.url.rsplit("/", 1)[-1]
        return None

    def get_paypal_id(self, account_name: str) -> str:
        """
        Get the ID of PayPal account on freeagent

        :param account_name: name of the account to find

        :return: ID of the named PayPal account or None
        """
        params = {"view": "paypal_accounts"}
        response = self.parent.get_api("bank_accounts", params)
        return self._find_bank_id(response, account_name)

    def get_first_paypal_id(self) -> str:
        """
        Get the ID of the first PayPal account on freeagent

        :return: ID of the first PayPal account or None if there is no PayPal account
        """
        params = {"view": "paypal_accounts"}
        response = self.parent.get_api("bank_accounts", params)
        if response:
            return response[0].url.rsplit("/", 1)[-1]
        return None

    def get_id(self, account_name: str) -> str:
        """
        Get the ID of account_name searching standard bank accounts

        :param account_name: name of the account to find

        :return: ID of the account or None if not found
        """
        params = {"view": "standard_bank_accounts"}
        response = self.parent.get_api("bank_accounts", params)
        return self._find_bank_id(response, account_name)

    def get_primary(self):
        """
        Get the ID of the primary bank account on freeagent (current account)

        :return: ID of the account or None if not found
        """
        params = {"view": "standard_bank_accounts"}
        response = self.parent.get_api("bank_accounts", params)
        for acct in response:
            if getattr(acct, "is_primary", False):
                return acct.url.rsplit("/", 1)[-1]
        return None

    def get_primary_uri(self):
        """
        Get the uri for the primary bank account on freeagent (current account)

        :return: uri of the account or None if not found
        """
        params = {"view": "standard_bank_accounts"}
        response = self.parent.get_api("bank_accounts", params)
        for acct in response:
            if getattr(acct, "is_primary", False):
                return acct.url
        return None
