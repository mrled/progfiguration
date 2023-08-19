"""Utility functions for progfiguration"""

import hashlib
import importlib
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
import importlib.resources
import importlib.util
import os
import sys
from typing import Optional

import progfiguration
from progfiguration.progfigtypes import AnyPathOrStr


def import_module_from_filepath(filepath: AnyPathOrStr, set_as_progfigsite: bool = False):
    """Import a module from a filesystem path

    Imported modules must have a unique name.
    This function will generate a unique name for the module by hashing the path.

    Args:

    ``filepath``:
        The path to the module, eg "/path/to/module.py"

    ``set_as_progfigsite``:
        If True, set the imported module as the progfigsite module
        (`progfiguration.progfigsite_module_path`.)
        This happens after we find the module and generate a name,
        but before we import the module.
        Progfigsite packages sometimes import core progfigsite in their __init__.py,
        including sitewrapper, which needs to know the progfigsite module,
        or else it will try to import the default progfigsite package name.
        Basically, this is only necessary if the module you are importing
        is a progfigsite package.

    Returns:
        A tuple of `(module, module_name)`,
        where the `module_name` is a hash of the filesystem path.
    """

    if type(filepath) is not str:
        filepath = str(filepath)
    filepath = os.path.realpath(os.path.normpath(filepath))

    # spec_from_file_location() will fail if the filepath is a directory,
    # but if the directory is a package, we can use its __init__.py file.
    if os.path.exists(f"{filepath}/__init__.py"):
        filepath = f"{filepath}/__init__.py"

    module_name = hashlib.md5(filepath.encode("utf-8")).hexdigest()

    if set_as_progfigsite:
        progfiguration.progfigsite_module_path = module_name

    if module_name in sys.modules:
        # We've already imported this one, just return it
        return (sys.modules[module_name], module_name)

    spec: Optional[ModuleSpec] = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None:
        raise ImportError(f"Could not import site package from {filepath}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    loader: Optional[Loader] = spec.loader
    if loader is None:
        raise ImportError(f"Could not import site package from {filepath}")

    loader.exec_module(module)
    return (module, module_name)
