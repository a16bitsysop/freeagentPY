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

        :return: id url of the category or None if not found
        """
        self._prep_categories()
        for _, cats in self.categories.items():
            for cat in cats:
                if description.lower() in cat.get("description", "").lower():
                    return cat["url"]
        return None

    def get_desc_nominal_code(self, description: str) -> ints:
        """
        Return the nominal code for a given category description.

        :param description: The description of the category.
        :return: The nominal code of the category, or None if not found.
        """
        self._prep_categories()
        for _, cats in self.categories.items():
            for cat in cats:
                if description.lower() in cat.get("description", "").lower():
                    return cat["nominal_code"]
        return None

    def get_nominal_code_id(self, nominal_code: int) -> str:
        """
        Get category id from nominal code

        :param nominal_code: nominal code of category to find

        :return: id url of the category or None if not found
        """
        self._prep_categories()
        for _, cats in self.categories.items():
            for cat in cats:
                if str(nominal_code) == cat.get("nominal_code", ""):
                    return cat["url"]
        return None
