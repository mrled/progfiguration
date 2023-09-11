"""Validate progfigsite modules

Progfigsite modules must follow a certain API.
This module validates compliance.
"""


from dataclasses import dataclass
import importlib
from types import ModuleType
from typing import Any, Callable, List

import progfiguration
from progfiguration.inventory.invstores import HostStore, SecretStore


@dataclass
class ProgfigsiteProperty:
    """A property of a progfigsite module."""

    submodule: str
    """The name of the submodule that the attribute is in.

    An empty string for the root module.
    """

    attribute: str
    """The string name of the attribute in the module to check for.

    If this is empty, we just check if the module exists.
    """

    type: Any
    """The type of the attribute."""

    required: bool = True
    """Whether the attribute is required."""

    @property
    def errstr(self) -> str:
        """A string describing the error"""
        proppath_arr = []
        if self.submodule:
            proppath_arr.append(self.submodule)
        if self.attribute:
            proppath_arr.append(self.attribute)
        proppath = ".".join(proppath_arr)
        return f"Module has no {proppath} attribute of type {self.type.__name__}"


class ValidationResult:
    """The result of validating a module"""

    # NOTE: When changing these properties, make corresponding changes in:
    #   1. src/progfiguration/newsite/__init__.py
    #   2. docs/src/getting-started/new-site.rst
    valid_properties = [
        ProgfigsiteProperty("", "site_name", str),
        ProgfigsiteProperty("", "site_description", str),
        ProgfigsiteProperty("", "get_version", Callable[[], str]),
        ProgfigsiteProperty("builddata", "", ModuleType),
        ProgfigsiteProperty("groups", "", ModuleType),
        ProgfigsiteProperty("nodes", "", ModuleType),
        ProgfigsiteProperty("roles", "", ModuleType),
        ProgfigsiteProperty("sitelib", "", ModuleType, required=False),
        ProgfigsiteProperty("inventory", "", ModuleType),
        ProgfigsiteProperty("inventory", "mint_version", Callable[[bool], str]),
        ProgfigsiteProperty("inventory", "hoststore", HostStore),
        ProgfigsiteProperty("inventory", "secretstore", SecretStore),
    ]
    """A list of attributes that a progfigsite module must have"""

    def __init__(self, path: str):

        self.path = path
        """The path to the module (must already be present in Python module path)"""

        self.errors: List[ProgfigsiteProperty] = []
        """A list of errors that were found"""

    @property
    def is_valid(self) -> bool:
        """True if the module is valid, False otherwise"""
        return len(self.errors) == 0


def validate(module_path: str) -> ValidationResult:
    """Validate a progfigsite module

    Return a `ValidationResult` object.
    """
    result = ValidationResult(module_path)
    module = importlib.import_module(module_path)
    imported = {}

    for prop in ValidationResult.valid_properties:
        if prop.submodule == "":
            imported[""] = module
        else:
            try:
                if prop.submodule not in imported:
                    imported[prop.submodule] = importlib.import_module(f"{module_path}.{prop.submodule}")
            except ImportError:
                if prop.required:
                    result.errors.append(prop)
                continue
        property_module = imported[prop.submodule]
        if prop.attribute == "" and prop.type == ModuleType:
            continue
        else:
            if not hasattr(property_module, prop.attribute) and prop.required:
                result.errors.append(prop)

    return result
