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
import os
from pathlib import Path
import sys
from types import ModuleType

import progfiguration


class ProgfigsiteModuleNotFoundError(ModuleNotFoundError):
    """Raised when the progfigsite module cannot be found"""

    pass


"""A cached reference to the progfigsite module"""
_progfigsite_module = None


def get_progfigsite() -> ModuleType:
    """The progfigsite module

    Returns:
        The progfigsite module
    """
    global _progfigsite_module
    if _progfigsite_module is None:
        try:
            _progfigsite_module = importlib.import_module(progfiguration.progfigsite_module_path)
        except ModuleNotFoundError as e:
            raise ProgfigsiteModuleNotFoundError(
                f"Could not find progfigsite module at {progfiguration.progfigsite_module_path}"
            ) from e
    return _progfigsite_module


def set_site_module_filepath(filepath: str):
    """Use a Python package from a filepath as progfigsite

    This is intended to be called only once, at the beginning of program execution.

    Args:
        filepath: The path to the site package, eg "/path/to/my_progfigsite"
    """
    progfiguration.progfigsite_module_path = "set_site_module_path_progfigsite"

    # spec_from_file_location() will fail if the filepath is a directory,
    # but if the directory is a package, we can use its __init__.py file.
    if os.path.exists(f"{filepath}/__init__.py"):
        filepath = f"{filepath}/__init__.py"

    spec = importlib.util.spec_from_file_location(progfiguration.progfigsite_module_path, filepath)
    if spec is None:
        raise ImportError(f"Could not import site package from {filepath}")
    progfigsite = importlib.util.module_from_spec(spec)
    sys.modules[progfiguration.progfigsite_module_path] = progfigsite
    spec.loader.exec_module(progfigsite)


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
    return Path(get_progfigsite().__file__).parent.resolve()
