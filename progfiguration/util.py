"""Progfiguration site wrapper

We keep a Python package path to the progfigsite module in progfiguration/__init__.py.
Using that, wrapper functions in this module can find and import the module.
If we can't find a module with that path, raise ProgfigsiteModuleNotFoundError.

Provide functions for retrieving site-specific resources,
including submodules and data files.
All progfiguration core code should use these functions to access site resources.
"""

import hashlib
import importlib
import importlib.resources
import importlib.util
import os
import sys

from progfiguration.progfigtypes import AnyPathOrStr


def import_module_from_filepath(filepath: AnyPathOrStr):
    """Import a module from a filesystem path

    Args:
        filepath: The path to the site package, eg "/path/to/package"

    Returns:
        A tuple of (module, module_name),
        where the module_name is a hash of the filesystem path.
    """

    if type(filepath) is not str:
        filepath = str(filepath)
    filepath = os.path.realpath(os.path.normpath(filepath))

    # spec_from_file_location() will fail if the filepath is a directory,
    # but if the directory is a package, we can use its __init__.py file.
    if os.path.exists(f"{filepath}/__init__.py"):
        filepath = f"{filepath}/__init__.py"

    module_name = hashlib.md5(filepath.encode("utf-8")).hexdigest()

    if module_name in sys.modules:
        # We've already imported this one, just return it
        return (sys.modules[module_name], module_name)

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None:
        raise ImportError(f"Could not import site package from {filepath}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return (module, module_name)