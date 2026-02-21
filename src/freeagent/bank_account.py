"""
Class for getting freeagent bank accounts
bank accounts are cached after first run
"""

from .base import FreeAgentBase


class BankAccountAPI(FreeAgentBase):
    """
    The BankAccountAPI class
    """

    def __init__(self, parent):  # pylint: disable=super-init-not-called
        """
        Initialize the class
        """
        self.parent = parent  # the main FreeAgent instance
        self._bank_accounts = None

    @property
    def bank_accounts(self):
        """
        Property to lazy load bank accounts
        """
        if self._bank_accounts is None:
            self._bank_accounts = self.parent.get_api("bank_accounts")
        return self._bank_accounts

    @bank_accounts.setter
    def bank_accounts(self, value):
        """
        Setter for bank accounts
        """
        self._bank_accounts = value

    def get_id_by_name(self, name: str, account_type: str = None) -> str:
        """
        Get the ID of a bank account by name

        :param name: name of the account to find
        :param account_type: optional type of account to filter by

        :return: ID of the account or None if not found
        """
        if account_type:
            account_type = account_type.replace("Account", "")

        for acct in self.bank_accounts:
            if acct.name.lower() == name.lower():
                if account_type and not acct.type.startswith(account_type):
                    continue
                return acct.url.rsplit("/", 1)[-1]
        return None

    def get_name_by_id(self, bank_id: str) -> str:
        """
        Get the bank account name for a bank account id

        :param bank_id: the bank account id to find

        :return: the name of the bank account
        :raises ValueError: if bank account not found
        """
        bank_id_str = str(bank_id)
        for acct in self.bank_accounts:
            if acct.url.rsplit("/", 1)[-1] == bank_id_str:
                return acct.name
        raise ValueError(f"Bank account with ID '{bank_id}' not found.")

    def get_name_by_uri(self, uri: str) -> str:
        """
        Get the bank account name for a bank account uri

        :param uri: the bank account uri to find

        :return: the name of the bank account
        :raises ValueError: if bank account not found
        """
        for acct in self.bank_accounts:
            if acct.url == uri:
                return acct.name
        raise ValueError(f"Bank account with URI '{uri}' not found.")

    def get_first_id_by_type(self, account_type: str) -> str:
        """
        Get the ID of the first account of a certain type

        :param account_type: type to search (e.g. 'PaypalAccount')

        :return: ID of the first account or None
        """
        account_type = account_type.replace("Account", "")
        for acct in self.bank_accounts:
            if acct.type.startswith(account_type):
                return acct.url.rsplit("/", 1)[-1]
        return None

    def get_primary_id(self) -> str:
        """
        Get the ID of the primary bank account

        :return: ID of the account or None
        """
        url = self.get_primary_url()
        if url:
            return url.rsplit("/", 1)[-1]
        return None

    def get_primary_url(self) -> str:
        """
        Get the url for the primary bank account

        :return: url of the account or None
        """
        for acct in self.bank_accounts:
            if acct.is_primary:
                return acct.url
        return None

    def get_paypal_id(self, account_name: str) -> str:
        """
        Get the ID of PayPal account on freeagent

        :param account_name: name of the account to find

        :return: ID of the named PayPal account or None
        """
        return self.get_id_by_name(account_name, "PaypalAccount")

    def get_first_paypal_id(self) -> str:
        """
        Get the ID of the first PayPal account on freeagent

        :return: ID of the first PayPal account or None if there is no PayPal account
        """
        return self.get_first_id_by_type("PaypalAccount")

    def get_id(self, account_name: str) -> str:
        """
        Get the ID of account_name searching standard bank accounts

        :param account_name: name of the account to find

        :return: ID of the account or None if not found
        """
        return self.get_id_by_name(account_name, "StandardBankAccount")
