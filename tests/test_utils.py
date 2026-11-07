"""
Unit tests for the utility functions in freeagent.utils.
"""

# pylint: disable=protected-access, too-few-public-methods
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from freeagent.utils import (
    _infer_type,
    list_to_dataclasses,
    make_dataclass_from_dict,
    singularize,
)


class SingularizeTest(unittest.TestCase):
    """Tests for the singularize helper."""

    def test_regular_plurals(self):
        """Test common plural endpoint keys are singularized."""

        self.assertEqual(singularize("bank_transactions"), "bank_transaction")
        self.assertEqual(singularize("bank_accounts"), "bank_account")

    def test_ies_and_es_endings(self):
        """Test 'ies' and 'es' plural endings."""

        self.assertEqual(singularize("categories"), "category")
        self.assertEqual(singularize("addresses"), "address")
        self.assertEqual(singularize("statuses"), "status")

    def test_singular_unchanged(self):
        """Test singular words are left unchanged."""

        self.assertEqual(singularize("business"), "business")


class InferTypeTest(unittest.TestCase):
    """Tests for the _infer_type helper."""

    def test_bool_not_int(self):
        """Test bool is not mis-inferred as int."""

        self.assertEqual(_infer_type(True), bool)
        self.assertEqual(_infer_type(1), int)

    def test_datetime_strings(self):
        """Test ISO-ish strings infer as datetime."""

        self.assertEqual(_infer_type("2023-01-01T12:30:00Z"), datetime)
        self.assertEqual(_infer_type("2023-01-01T12:30:00+01:00"), datetime)

    def test_date_and_decimal(self):
        """Test date and decimal strings infer correctly."""

        self.assertEqual(_infer_type("2023-01-01"), date)
        self.assertEqual(_infer_type("1.50"), Decimal)
        self.assertEqual(_infer_type(1.5), Decimal)

    def test_plain_string(self):
        """Test plain strings stay str."""

        self.assertEqual(_infer_type("hello"), str)


class MakeDataclassTest(unittest.TestCase):
    """Tests for dynamic dataclass creation with type conversion."""

    def test_converts_with_inferred_types(self):
        """Test type conversion on dynamic dataclass creation."""

        data = {
            "id": 1,
            "amount": "12.50",
            "dated_on": "2023-01-15",
            "created_at": "2023-01-15T10:00:00Z",
            "is_primary": True,
            "nested": {"x": 1},
        }
        obj = make_dataclass_from_dict("BankAccount", data)
        self.assertEqual(obj.amount, Decimal("12.50"))
        self.assertEqual(obj.dated_on, date(2023, 1, 15))
        self.assertEqual(
            obj.created_at,
            datetime(2023, 1, 15, 10, 0, tzinfo=timezone.utc),
        )
        self.assertIs(obj.is_primary, True)
        self.assertEqual(obj.nested, {"x": 1})

    def test_none_values_stay_none(self):
        """Test None values are kept as None."""

        obj = make_dataclass_from_dict("BankAccount", {"id": 1, "amount": None})
        self.assertIsNone(obj.amount)

    def test_skips_non_identifier_keys(self):
        """Test keys that are not valid identifiers are skipped."""

        obj = make_dataclass_from_dict("Thing", {"a-b": 1, "ok": 2})
        self.assertEqual(obj.ok, 2)
        self.assertFalse(hasattr(obj, "a-b"))

    def test_list_to_dataclasses_filters_non_dicts(self):
        """Test non-dict entries are filtered out."""

        objs = list_to_dataclasses("Category", [{"id": 1}, {"id": 2}, "not-a-dict"])
        self.assertEqual(len(objs), 2)


if __name__ == "__main__":
    unittest.main()
