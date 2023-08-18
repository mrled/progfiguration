"""Progfiguration site wrapper

We keep a Python package path to the progfigsite module in progfiguration/__init__.py.
Using that, wrapper functions in this module can find and import the module.
If we can't find a module with that path, raise ProgfigsiteModuleNotFoundError.

Provide functions for retrieving site-specific resources,
including submodules and data files.
All progfiguration core code should use these functions to access site resources.
"""

import importlib
import importlib.resources
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Optional

import progfiguration
from progfiguration.util import import_module_from_filepath


class ProgfigsiteModuleNotFoundError(ModuleNotFoundError):
    """Raised when the progfigsite module cannot be found"""

    pass


"""A cached reference to the progfigsite module"""
_progfigsite_module: Optional[ModuleType] = None


def get_progfigsite() -> ModuleType:
    """The progfigsite module

    Returns:
        The progfigsite module
    """
    global _progfigsite_module
    if _progfigsite_module is None:
        progfiguration.logger.debug("Loading progfigsite module")
        try:
            _progfigsite_module = importlib.import_module(progfiguration.progfigsite_module_path)
            progfiguration.logger.debug(f"Loaded progfigsite module at {progfiguration.progfigsite_module_path}")
        except ModuleNotFoundError as e:
            progfiguration.logger.debug(
                f"Could not find progfigsite module at {progfiguration.progfigsite_module_path}"
            )
            raise ProgfigsiteModuleNotFoundError(
                f"Could not find progfigsite module at {progfiguration.progfigsite_module_path}"
            ) from e
    else:
        progfiguration.logger.debug(
            f"Using already-loaded progfigsite module from {progfiguration.progfigsite_module_path}"
        )
    return _progfigsite_module


def site_modpath(submodule_path: str) -> str:
    """The full path to a site submodule

    Args:
        submodule_path: The path to the submodule, relative to the site package.
            This can be an empty string for the site package itself,
            or a dotted path to a submodule.
            E.g. "", "nodes", "nodes.example_node"
    """
    if submodule_path:
        modpath = f"{progfiguration.progfigsite_module_path}.{submodule_path}"
    else:
        modpath = progfiguration.progfigsite_module_path
    progfiguration.logger.debug(f"site_modpath({submodule_path}) = {modpath}")
    return modpath


def site_submodule(submodule_path: str) -> ModuleType:
    """The Python module for a given site submodule

    Args:
        submodule_path: The path to the submodule, relative to the site package.
            This can be an empty string for the site package itself,
            or a dotted path to a submodule.
            E.g. "", "nodes", "nodes.example_node"

    Raises:
        ModuleNotFoundError: If the submodule does not exist
            (not ImportError!)
    """
    module = importlib.import_module(site_modpath(submodule_path))
    return module


def site_submodule_resource(submodule_path: str, resource_name: str):
    """A resource from a site submodule

    Similar to site_submodule(),
    but returns a resource from the submodule.

    Args:
        submodule_path: The path to the submodule, relative to the site package.
            This can be an empty string if the resource is in the site package itself,
            or a dotted path to a submodule.
            E.g. "", "nodes", "nodes.example_node"
        resource_name: The name of the resource file.
            E.g. "inventory.yml", "secrets.yml"

    Raises:
        ModuleNotFoundError: If the submodule does not exist
            (not ImportError!)
    """
    return importlib.resources.files(site_modpath(submodule_path)).joinpath(resource_name)


def get_progfigsite_path() -> Path:
    """The filesystem path to the progfigsite package

    Returns:
        The path to the progfigsite package, as a string.
    """
    progfigsite_module = get_progfigsite()
    if progfigsite_module.__file__ is None:
        raise ProgfigsiteModuleNotFoundError(
            f"Was able to import progfigsite module at {progfiguration.progfigsite_module_path}, but its __file__ attribute is None."
        )
    return Path(progfigsite_module.__file__).parent.resolve()
