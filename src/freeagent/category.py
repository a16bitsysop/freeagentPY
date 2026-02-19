"""
Class for getting freeagent categories
categories are cached after first run
"""

from .base import FreeAgentBase
from .utils import list_to_dataclasses


class CategoryAPI(FreeAgentBase):
    """
    The CategoryAPI class
    """

    def __init__(self, parent):  # pylint: disable=super-init-not-called
        """
        Initialize the class
        """
        self.parent = parent  # the main FreeAgent instance
        self._categories = None

    @property
    def categories(self):
        """
        Property to lazy load categories
        """
        if self._categories is None:
            response = self.parent.get_api("categories")
            if not response:
                return []

            container = response[0]
            self._categories = []
            for value in vars(container).values():
                if isinstance(value, list):
                    self._categories.extend(list_to_dataclasses("Category", value))
        return self._categories

    @categories.setter
    def categories(self, value):
        """
        Setter for categories
        """
        self._categories = value

    def get_desc_id(self, description: str) -> str:
        """
        Return the category id url for passed category name

        :param description: name of category to find

        :return: id url of the category
        :raises ValueError: if category not found
        """
        for cat in self.categories:
            if description.lower() in cat.description.lower():
                return cat.url
        raise ValueError(f"Category with description '{description}' not found.")

    def get_desc_nominal_code(self, description: str) -> str:
        """
        Return the nominal code for a given category description

        :param description: The description of the category

        :return: The nominal code of the category
        :raises ValueError: if category not found
        """
        for cat in self.categories:
            if description.lower() in cat.description.lower():
                return cat.nominal_code
        raise ValueError(f"Category with description '{description}' not found.")

    def get_nominal_code_id(self, nominal_code: int) -> str:
        """
        Get category id url from nominal code

        :param nominal_code: nominal code of category to find

        :return: id url of the category
        :raises ValueError: if category not found
        """
        for cat in self.categories:
            if str(nominal_code) == cat.nominal_code:
                return cat.url
        raise ValueError(f"Category with nominal code '{nominal_code}' not found.")

    def get_nominal_name(self, nominal_code: int) -> str:
        """
        Get category name from nominal code

        :param nominal_code: nominal code of category to find

        :return: name (description) of the category
        :raises ValueError: if category not found
        """
        for cat in self.categories:
            if str(nominal_code) == cat.nominal_code:
                return cat.description
        raise ValueError(f"Category with nominal code '{nominal_code}' not found.")
