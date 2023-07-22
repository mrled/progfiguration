"""Validate progfigsite modules

Progfigsite modules must follow a certain API.
This module validates compliance.
"""


from dataclasses import dataclass
import importlib
from types import ModuleType
from typing import Any, Callable, List


@dataclass
class ProgfigsiteAttribute:
    """An attribute of a progfigsite module

    Attributes:
        path: The path of the attribute relative to the root module
        type: The type of the attribute
        required: Whether the attribute is required
    """

    path: str
    type: Any
    required: bool

    @property
    def errstr(self) -> str:
        """A string describing the error"""
        return f"Module has no {self.path} attribute"


class ValidationResult:
    """The result of validating a module

    Attributes:
        path: The path to the module (must be present in Python module path)
        errors: A list of errors that were found
    """

    valid_attributes = [
        ProgfigsiteAttribute("site_name", str, True),
        ProgfigsiteAttribute("site_description", str, True),
        ProgfigsiteAttribute("mint_version", Callable[[bool], str], True),
        ProgfigsiteAttribute("get_version", Callable[[], str], True),
        ProgfigsiteAttribute("autovendor", ModuleType, True),
        ProgfigsiteAttribute("builddata", ModuleType, True),
        ProgfigsiteAttribute("groups", ModuleType, True),
        ProgfigsiteAttribute("nodes", ModuleType, True),
        ProgfigsiteAttribute("roles", ModuleType, True),
        ProgfigsiteAttribute("sitelib", ModuleType, False),
    ]

    def __init__(self, path: str):
        self.path = path
        self.errors: List[ProgfigsiteAttribute] = []

    @property
    def is_valid(self) -> bool:
        """True if the module is valid, False otherwise"""
        return len(self.errors) == 0


def validate(module_path: str) -> ValidationResult:
    """Validate a module

    Return a ValidationResult object.
    """
    result = ValidationResult(module_path)
    module = importlib.import_module(module_path)

    for attribute in ValidationResult.valid_attributes:
        if attribute.type == ModuleType:
            try:
                importlib.import_module(f"{module_path}.{attribute.path}")
            except ImportError:
                if attribute.required:
                    result.errors.append(attribute)
        else:
            if not hasattr(module, attribute.path):
                result.errors.append(attribute)

    return result