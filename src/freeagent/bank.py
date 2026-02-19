"""
This module provides the BankAPI class to retreive information
about bank accounts on freeagent
"""

from base64 import b64encode
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .base import FreeAgentBase
from .payload import ExplanationPayload, UpdatePayload


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

    def explain_transaction(
        self, tx_obj: ExplanationPayload, printout: bool = True, dryrun: bool = False
    ):
        """
        Post the explanation to freeagent in the passed ExplanationPayload tx_obj

        :param tx_obj: ExplanationPayload to use
        :param printout: Print out the desciption and gross value
        :param dry_run: if True then do not post to freeagent, only print details
        """
        json_data = self.serialize_for_api(tx_obj)

        if printout:
            print(json_data["description"], json_data.get("gross_value"))
        if not dryrun:
            self.parent.post_api(
                "bank_transaction_explanations",
                "bank_transaction_explanation",
                json_data,
            )

    def explain_update(
        self,
        url: str,
        tx_obj: ExplanationPayload,
        printout: bool = True,
        dryrun: bool = False,
    ):
        """
        Update an existing explanation on freeagent with the passed url

        :param url: url attribute of the bank transaction explanation to change
        :param tx_obj: ExplanationPayload to use for updating the explanation
        :param printout: Print out the desciption and gross value
        :param dry_run: if True then do not post to freeagent, only print details
        """
        json_data = self.serialize_for_api(tx_obj)

        if printout:
            print(json_data["description"], json_data.get("gross_value"))
        if not dryrun:
            self.parent.put_api(url, "bank_transaction_explanation", json_data)

    def explain_list(self, items: list, dryrun: bool = False, separator: str = None):
        """
        Iterate through a list of UpdatePayload or ExplanationPayload and call
        explain_update or explain_transaction accordingly.

        :param items: list of UpdatePayload or ExplanationPayload objects
        :param dryrun: if True then do not post to freeagent, only print details
        :param separator: optional string to replace with newlines in description for table output
        """
        table = Table(title="Explanation for transaction")
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")
        table.add_column("Amount", justify="right", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Type", style="blue")

        for item in items:
            if isinstance(item, UpdatePayload):
                payload = item.payload
                desc = "Update"
                bank = self.parent.get_api(
                    item.url.removeprefix(self.parent.api_base_url)
                )
                bank_uri = bank[0].bank_transaction_explanation["bank_account"]
                update = self.parent.bank_account.get_name_by_uri(bank_uri)
                table.title = f"Explanation for {update} transaction"
                self.explain_update(item.url, payload, printout=False, dryrun=dryrun)

            elif isinstance(item, ExplanationPayload):
                payload = item
                desc = "New"
                self.explain_transaction(item, printout=False, dryrun=dryrun)

            else:
                raise ValueError(f"Unknown item type: {type(item)}")

            if getattr(payload, "transfer_bank_account", None):
                category_display = "Transfer"
            else:
                category_display = self.parent.category.get_nominal_name(
                    payload.nominal_code
                )
            description = (
                (payload.description or "").replace(separator, "\n")
                if separator
                else payload.description
            )
            table.add_row(
                str(payload.dated_on),
                description,
                str(payload.gross_value),
                category_display,
                desc,
            )
        console = Console()
        console.print(table)

    def get_unexplained_transactions(self, account_id: str) -> list:
        """
        Return a list of unexplained transaction objects for the bank account with id of account_id

        :param account_id: account id to use, or the whole url

        :return: list of the unexplained transactions
        """
        if not account_id.startswith("http"):
            account_id = f"{self.parent.api_base_url}bank_accounts/{account_id}"

        params = {"bank_account": account_id, "view": "unexplained"}
        return self.parent.get_api("bank_transactions", params)
