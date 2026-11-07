"""This module provides utility functions for the FreeAgent API client."""

from dataclasses import asdict, is_dataclass, make_dataclass
from decimal import Decimal
from datetime import date, datetime
from functools import lru_cache
from typing import Optional, Any
import keyword
import re


def _infer_type(value: Any) -> Any:
    """
    Infer the type of a value

    :param value: The value to guess the type of

    :return: The type of the value
    """
    inferred_type = Any
    if isinstance(value, bool):
        inferred_type = bool
    elif isinstance(value, int):
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
    """
    Convert a value to a target type

    :param value: The value to convert
    :param target_type: The type to convert to

    :return: The converted value
    """
    if value is None:
        return None
    if target_type is Decimal:
        return Decimal(value)
    if target_type is date:
        return datetime.strptime(value, "%Y-%m-%d").date()
    if target_type is datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def _field_name(name: str) -> str:
    """
    Return a dataclass-safe field name, adding a trailing underscore to keywords

    :param name: the key from the API response

    :return: the field name to use on the dataclass
    """
    return f"{name}_" if keyword.iskeyword(name) else name


@lru_cache(maxsize=None)
def _dataclass_for(class_name: str, fields: tuple) -> type:
    """
    Return the dataclass for a name and field set, creating it once and reusing it

    :param class_name: The name to use for the dataclass
    :param fields: tuple of (name, type, default) entries

    :return: the dataclass type
    """
    return make_dataclass(class_name, list(fields))


def make_dataclass_from_dict(class_name: str, data: dict, field_types: dict = None):
    """
    Dynamically create a dataclass from a dictionary, with optional type conversions.

    Dataclasses are cached by name and fields, so items with the same shape share a class.

    :param class_name: The name to use for the dataclass
    :param data: The data to turn into a dataclass
    :param field_types: dict of types for the data
    """
    if field_types is None:
        field_types = {}

    inferred_types = {
        key: _infer_type(value) for key, value in data.items() if key not in field_types
    }
    final_field_types = {**inferred_types, **field_types}

    fields_to_create = tuple(
        (_field_name(name), Optional[f_type], None)
        for name, f_type in final_field_types.items()
        if name.isidentifier()
    )

    data_class = _dataclass_for(class_name, fields_to_create)

    converted_data = {
        _field_name(key): _convert_value(value, final_field_types.get(key))
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


def serialize_for_api(obj) -> dict:
    """
    Convert dataclasses or dicts with Decimal, date, etc. into plain API-compatible dicts

    :param obj: dataclass or dict to convert

    :return: API-compatible dict
    """
    if is_dataclass(obj):
        obj = asdict(obj)

    def convert(val):
        if isinstance(val, Decimal):
            return str(val)
        if isinstance(val, (date, datetime)):
            return val.isoformat()
        if isinstance(val, dict):
            return {k: convert(v) for k, v in val.items()}
        if isinstance(val, list):
            return [convert(i) for i in val]
        return val

    return {k: convert(v) for k, v in obj.items() if v is not None}


def singularize(word: str) -> str:
    """
    Return a singular form of a plural API key for use as a class name.

    Handles the common English plural endings returned by the FreeAgent API:
    'ies' -> 'y', and 'ses'/'xes'/'zes'/'ches'/'shes' drop 'es'.

    :param word: plural word to singularize (e.g. 'bank_transactions')

    :return: singular form (e.g. 'bank_transaction')
    """
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith(("ses", "xes", "zes", "ches", "shes")):
        return word[:-2]
    if word.endswith("ss"):
        return word
    return word.rstrip("s")


def list_to_dataclasses(class_name: str, data_list: list) -> list:
    """
    Convert a list of dictionaries to a list of dataclasses

    :param class_name: name of the dataclass
    :param data_list: list of dictionaries

    :return: list of dataclasses
    """
    return [
        make_dataclass_from_dict(class_name, item)
        for item in data_list
        if isinstance(item, dict)
    ]
