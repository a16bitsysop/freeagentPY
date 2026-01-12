"""
Class for getting freeagent categories
categories are cached after first run
"""

from .base import FreeAgentBase


class CategoryAPI(FreeAgentBase):
    """
    The CategoryAPI class
    """

    def __init__(self, parent):  # pylint: disable=super-init-not-called
        """
        Initialize the class
        """
        self.parent = parent  # the main FreeAgent instance
        self.categories = {}

    def _prep_categories(self):
        """
        get the categories if not already done
        """
        if not self.categories:
            self.categories = self.parent.get_api("categories")

    def get_desc_id(self, description: str) -> str:
        """
        Return the description id for passed category name

        :param description: name of category to find

        :return: id url of the category
        :raises ValueError: if category not found
        """
        self._prep_categories()
        for cat in self.categories:
            if description.lower() in cat.description.lower():
                return cat.url
        raise ValueError(f"Category with description '{description}' not found.")

    def get_desc_nominal_code(self, description: str) -> str:
        """
        Return the nominal code for a given category description.

        :param description: The description of the category.

        :return: The nominal code of the category
        :raises ValueError: if category not found
        """
        self._prep_categories()
        for cat in self.categories:
            if description.lower() in cat.description.lower():
                return cat.nominal_code
        raise ValueError(f"Category with description '{description}' not found.")

    def get_nominal_code_id(self, nominal_code: int) -> str:
        """
        Get category id from nominal code

        :param nominal_code: nominal code of category to find

        :return: id url of the category
        :raises ValueError: if category not found
        """
        self._prep_categories()
        for cat in self.categories:
            if str(nominal_code) == cat.nominal_code:
                return cat.url
        raise ValueError(f"Category with nominal code '{nominal_code}' not found.")
