"""Progfiguration site wrapper

We keep a Python package path to the progfigsite module in progfiguration/__init__.py.
Using that, wrapper functions in this module can find and import the module.
If we can't find a module with that path, raise ProgfigsiteModuleNotFoundError.

Provide functions for retrieving site-specific resources,
including submodules and data files.
All progfiguration core code should use these functions to access site resources.
"""

import importlib
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
import importlib.resources
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Dict, Optional, Tuple

import progfiguration


class ProgfigsiteModuleNotSetError(ModuleNotFoundError):
    """Raised when the progfigsite module was not set"""

    pass


class ProgfigsiteModuleNotFoundError(ModuleNotFoundError):
    """Raised when the progfigsite module cannot be found"""

    pass


_sitewrapper_cache: Dict[str, Any] = {}
"""A private cache for the sitewrapper module

Should only be accessed by getters and setters in the sitewrapper module.
"""


def get_progfigsite() -> Tuple[str, ModuleType]:
    """Return a tuple of the progfigsite module name and module

    Raises:

    `ProgfigsiteModuleNotSetError`
        If the progfigsite module was not set
    """
    global _sitewrapper_cache
    if "module" not in _sitewrapper_cache or "name" not in _sitewrapper_cache:
        raise ProgfigsiteModuleNotSetError("The progfigsite module was not set.")
    return (_sitewrapper_cache["name"], _sitewrapper_cache["module"])


def set_progfigsite_by_filepath(filepath: Path, module_name: str):
    """Set the progfigsite module by its filesystem path.

    Args:

    ``filepath``:
        The path to the module, eg "/path/to/module.py".

    ``module_name``:
        The name of the module, eg "example_site".

        Should match the package name so that 'import module_name.submodule' works.
    """

    global _sitewrapper_cache

    filepath = filepath.resolve().absolute()

    # spec_from_file_location() will fail if the filepath is a directory,
    # but if the directory is a package, we can use its __init__.py file.
    if filepath.is_dir():
        if (filepath / "__init__.py").exists():
            filepath = filepath / "__init__.py"
        else:
            raise ProgfigsiteModuleNotFoundError(f"Could not find progfigsite module at {filepath}")

    old_module = _sitewrapper_cache.get("module", None)
    old_name = _sitewrapper_cache.get("name", None)

    try:

        spec: Optional[ModuleSpec] = importlib.util.spec_from_file_location(module_name, filepath)
        if spec is None:
            raise ProgfigsiteModuleNotFoundError(f"Could not generate spec for site package from {filepath}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        loader: Optional[Loader] = spec.loader
        if loader is None:
            raise ProgfigsiteModuleNotFoundError(f"Could not load spec for site package from {filepath}")

        # When the module is loaded, it might end up calling code that calls sitewrapper.get_progfigsite().
        # We need to make sure that the module is in the cache before that happens.
        _sitewrapper_cache["module"] = module
        _sitewrapper_cache["name"] = module_name

        loader.exec_module(module)

        # Not sure if we have to set this again after exec_module().
        _sitewrapper_cache["module"] = module

    except BaseException as exc:

        # If we failed to load the module, we need to restore the old module in the cache.
        # Otherwise, the next call to get_progfigsite() will return the new module,
        # even though it failed to load.
        if old_module is None:
            del _sitewrapper_cache["module"]
        else:
            _sitewrapper_cache["module"] = old_module
        if old_name is None:
            del _sitewrapper_cache["name"]
        else:
            _sitewrapper_cache["name"] = old_name

        raise ProgfigsiteModuleNotFoundError(f"Could not load site package from {filepath}") from exc

    return _sitewrapper_cache["module"]


def set_progfigsite_by_module_name(module_name: str):
    """Set the progfigsite module by its module name.

    The module must already be present in the Python path.
    """
    global _sitewrapper_cache
    try:
        module = importlib.import_module(module_name)
        _sitewrapper_cache["module"] = module
        _sitewrapper_cache["name"] = module_name
        progfiguration.logger.debug(f"Loaded progfigsite module at {module_name}")
    except ModuleNotFoundError as e:
        progfiguration.logger.debug(f"Could not find progfigsite module at {module_name}")
        raise ProgfigsiteModuleNotFoundError(f"Could not find progfigsite module at {module_name}") from e
    return _sitewrapper_cache["module"]


def site_modpath(submodule_path: str) -> str:
    """The full path to a site submodule

    Args:
        submodule_path: The path to the submodule, relative to the site package.
            This can be an empty string for the site package itself,
            or a dotted path to a submodule.
            E.g. "", "nodes", "nodes.example_node"
    """
    name, module = get_progfigsite()
    if submodule_path:
        modpath = f"{name}.{submodule_path}"
    else:
        modpath = name
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
    name, module = get_progfigsite()
    if module.__file__ is None:
        raise ProgfigsiteModuleNotFoundError(
            f"Was able to import progfigsite module at {name}, but its __file__ attribute is None."
        )
    return Path(module.__file__).parent.resolve()
