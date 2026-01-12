"""This module provides utility functions for the FreeAgent API client."""

from dataclasses import make_dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, Any
import re


def _infer_type(value: Any) -> Any:
    """Infer the type of a value."""
    inferred_type = Any
    if isinstance(value, int):
        inferred_type = int
    elif isinstance(value, float):
        inferred_type = Decimal
    elif isinstance(value, str):
        if re.fullmatch(r"^-?\d+\.\d+$", value):
            inferred_type = Decimal
        elif re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", value):
            inferred_type = date
        elif re.fullmatch(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$",
            value,
        ):
            inferred_type = datetime
        else:
            inferred_type = str
    elif isinstance(value, dict):
        inferred_type = dict
    elif isinstance(value, list):
        inferred_type = list
    return inferred_type


def _convert_value(value: Any, target_type: Any) -> Any:
    """Convert a value to a target type."""
    if value is None:
        return None
    if target_type is Decimal:
        return Decimal(value)
    if target_type is date:
        return datetime.strptime(value, "%Y-%m-%d").date()
    if target_type is datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def make_dataclass_from_dict(class_name, data: dict, field_types: dict = None):
    """
    Dynamically create a dataclass from a dictionary, with optional type conversions.
    """
    if field_types is None:
        field_types = {}

    inferred_types = {
        key: _infer_type(value) for key, value in data.items() if key not in field_types
    }
    final_field_types = {**inferred_types, **field_types}

    fields_to_create = [
        (name, Optional[f_type], None)
        for name, f_type in final_field_types.items()
        if name.isidentifier()
    ]

    data_class = make_dataclass(class_name, fields_to_create)

    converted_data = {
        key: _convert_value(value, final_field_types.get(key))
        for key, value in data.items()
        if key in final_field_types
    }

    return data_class(
        **{
            k: v
            for k, v in converted_data.items()
            if k in data_class.__dataclass_fields__
        }
    )
