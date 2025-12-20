"""
Unit tests for the CategoryAPI class using offline dummy data and mocks.
Verifies category caching, lookup by description, and lookup by nominal code.
"""

# pylint: disable=protected-access, too-few-public-methods
import unittest
from unittest.mock import MagicMock

from freeagent.category import CategoryAPI


class CategoryAPITestCase(unittest.TestCase):
    """
    Unit tests for the CategoryAPI class using MagicMock and dummy data.
    """

    def setUp(self):
        # Set up a mock parent with get_api
        self.parent = MagicMock()
        self.api = CategoryAPI(self.parent)
        self.dummy_categories = {
            "active": [
                {
                    "description": "Office Costs",
                    "url": "http://cat/1",
                    "nominal_code": "101",
                },
                {"description": "Travel", "url": "http://cat/2", "nominal_code": "202"},
            ],
            "archived": [
                {
                    "description": "Old Office",
                    "url": "http://cat/3",
                    "nominal_code": "303",
                },
            ],
        }

    def test_prep_categories_fetches_once(self):
        """Test that categories are fetched from the parent once and then cached."""
        self.parent.get_api.return_value = self.dummy_categories
        self.api._prep_categories()
        self.assertEqual(self.api.categories, self.dummy_categories)
        # Should not call get_api again if already cached
        self.api._prep_categories()
        self.parent.get_api.assert_called_once_with("categories")

    def test_get_desc_id_finds_description(self):
        """Test category lookup by description (case-insensitive, substring match)."""
        self.parent.get_api.return_value = self.dummy_categories
        url = self.api.get_desc_id("office costs")
        self.assertEqual(url, "http://cat/1")
        url = self.api.get_desc_id("Old office")
        self.assertEqual(url, "http://cat/3")
        # Case insensitive, substring match
        url = self.api.get_desc_id("Travel")
        self.assertEqual(url, "http://cat/2")
        # Not found
        url = self.api.get_desc_id("Nonexistent")
        self.assertIsNone(url)

    def test_get_nominal_id_finds_code(self):
        """Test category lookup by nominal code."""
        self.parent.get_api.return_value = self.dummy_categories
        url = self.api.get_nominal_id(101)
        self.assertEqual(url, "http://cat/1")
        url = self.api.get_nominal_id(303)
        self.assertEqual(url, "http://cat/3")
        url = self.api.get_nominal_id(999)
        self.assertIsNone(url)

    def test_caching_persists_for_getters(self):
        """Test that cached categories persist across lookups."""
        self.parent.get_api.return_value = self.dummy_categories
        # First call populates cache
        self.api.get_desc_id("Travel")
        # Change return value; should not affect already-cached results
        self.parent.get_api.return_value = {}
        url = self.api.get_desc_id("Office")
        self.assertEqual(url, "http://cat/1")


if __name__ == "__main__":
    unittest.main()
