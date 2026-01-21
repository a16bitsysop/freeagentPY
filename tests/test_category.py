"""
Unit tests for the CategoryAPI class using offline dummy data and mocks.
Verifies category caching, lookup by description, and lookup by nominal code.
"""

# pylint: disable=protected-access, too-few-public-methods
import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock

from freeagent.category import CategoryAPI


@dataclass
class MockContainer:
    """Mock container to simulate the API response structure."""

    admin_expenses_categories: list
    income_categories: list


class CategoryAPITestCase(unittest.TestCase):
    """
    Unit tests for the CategoryAPI class using MagicMock and dummy data.
    """

    def setUp(self):
        # Set up a mock parent with get_api
        self.parent = MagicMock()
        self.api = CategoryAPI(self.parent)

        # Data as dictionaries, as they come from the "API" container attributes
        self.cat1 = {
            "description": "Office Costs",
            "url": "http://cat/1",
            "nominal_code": "101",
        }
        self.cat2 = {
            "description": "Travel",
            "url": "http://cat/2",
            "nominal_code": "202",
        }
        self.cat3 = {
            "description": "Old Office",
            "url": "http://cat/3",
            "nominal_code": "303",
        }

        self.container = MockContainer(
            admin_expenses_categories=[self.cat1, self.cat2],
            income_categories=[self.cat3],
        )

        # get_api returns a list containing the container
        self.parent.get_api.return_value = [self.container]

    def test_prep_categories_fetches_once(self):
        """Test that categories are fetched from the parent once and then cached."""
        self.api._prep_categories()

        # Verify the categories were flattened and converted
        self.assertEqual(len(self.api.categories), 3)
        descriptions = sorted([c.description for c in self.api.categories])
        expected_descriptions = sorted(["Office Costs", "Travel", "Old Office"])
        self.assertEqual(descriptions, expected_descriptions)

        # Should not call get_api again if already cached
        self.api._prep_categories()
        self.parent.get_api.assert_called_once_with("categories")

    def test_get_desc_id_finds_description(self):
        """Test category lookup by description (case-insensitive, substring match)."""
        url = self.api.get_desc_id("office costs")
        self.assertEqual(url, "http://cat/1")
        url = self.api.get_desc_id("Old office")
        self.assertEqual(url, "http://cat/3")
        # Case insensitive, substring match
        url = self.api.get_desc_id("Travel")
        self.assertEqual(url, "http://cat/2")
        # Not found
        with self.assertRaises(ValueError):
            self.api.get_desc_id("Nonexistent")

    def test_get_nominal_id_finds_code(self):
        """Test category lookup by nominal code."""
        url = self.api.get_nominal_code_id(101)
        self.assertEqual(url, "http://cat/1")
        url = self.api.get_nominal_code_id(303)
        self.assertEqual(url, "http://cat/3")
        with self.assertRaises(ValueError):
            self.api.get_nominal_code_id(999)

    def test_caching_persists_for_getters(self):
        """Test that cached categories persist across lookups."""
        # First call populates cache
        self.api.get_desc_id("Travel")
        # Change return value; should not affect already-cached results
        self.parent.get_api.return_value = []
        url = self.api.get_desc_id("Office")
        self.assertEqual(url, "http://cat/1")


if __name__ == "__main__":
    unittest.main()
