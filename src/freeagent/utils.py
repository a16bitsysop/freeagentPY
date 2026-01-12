from dataclasses import make_dataclass, field
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, Any
import re


def make_dataclass_from_dict(class_name, data: dict, field_types: dict = None):
    """
    Dynamically create a dataclass from a dictionary, with optional type conversions.
    """
    if field_types is None:
        field_types = {}

    # Infer types from data if not explicitly provided
    inferred_types = {}
    for key, value in data.items():
        if key not in field_types:
            if isinstance(value, int):
                inferred_types[key] = int
            elif isinstance(value, float):
                inferred_types[key] = Decimal
            elif isinstance(value, str):
                if re.fullmatch(r"^-?\d+\.\d+$", value):
                    inferred_types[key] = Decimal
                elif re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", value):
                    inferred_types[key] = date
                elif re.fullmatch(
                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$",
                    value,
                ):
                    inferred_types[key] = datetime
                else:
                    inferred_types[key] = str
            elif isinstance(value, dict):
                inferred_types[key] = dict
            elif isinstance(value, list):
                inferred_types[key] = list
            else:
                inferred_types[key] = Any

    final_field_types = {**inferred_types, **field_types}

    # Create fields with type hints for the dataclass
    fields_to_create = []
    for name, f_type in final_field_types.items():
        if name.isidentifier():
            if (
                f_type is None or f_type is Optional[Any]
            ):  # Make all optional to handle missing data
                fields_to_create.append((name, Optional[Any], field(default=None)))
            else:
                fields_to_create.append((name, Optional[f_type], field(default=None)))

    DataClass = make_dataclass(class_name, fields_to_create)

    # Prepare data with type conversions
    converted_data = {}
    for key, value in data.items():
        if key in final_field_types:
            target_type = final_field_types[key]
            if value is not None:
                if target_type is Decimal:
                    converted_data[key] = Decimal(value)
                elif target_type is date:
                    converted_data[key] = datetime.strptime(value, "%Y-%m-%d").date()
                elif target_type is datetime:
                    # Handle 'Z' for UTC and ensure microsecond precision is optional
                    converted_data[key] = datetime.fromisoformat(
                        value.replace("Z", "+00:00")
                    )
                else:
                    converted_data[key] = value
            else:
                converted_data[key] = None
        else:
            converted_data[key] = value

    return DataClass(
        **{
            k: v
            for k, v in converted_data.items()
            if k in DataClass.__dataclass_fields__
        }
    )
