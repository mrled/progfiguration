"""Progfiguration site wrapper

Find a progfigsite package.
If there is a package called 'progfigsite' in the Python path, import that.
Otherwise, import the example site from the core progfiguration package.
Exactly once, at the beginning of program execution,
the user can call set_site_module_filepath() to use a custom site package,
which can have any name.

Provide functions for retrieving site-specific resources,
including submodules and data files.
All progfiguration core code should use these functions to access site resources.

(Why can't progfiguration core code use importlib.import_module()?
Doing that requires the full module path, like 'progfigsite' or 'something.else.my_site'.
We want to allow the progfigsite to have a dynamically determined name,
to enable fallback to example_progfigsite and the --progfigsite-package-path option.
Note that 'import X as progfigsite' does not mean that
'import_module("sitewrapper.progfigsite")' will work.)

## About site packages

Site packages must meet the following requirements:

Submodules:
    Required:
        - nodes
        - roles
        - groups
    Optional:
        - sitelib: not used by progfiguration, but can be used internally in the site package

Data files:
    Required:
        - inventory.conf

Variables exported from package root:
    Required:
        - site_name: An arbitrary string used to identify the site to users
    Optional:
        - site_description: A longer string describing the site

Other names are reserved for future use by progfiguration.
"""

import importlib
import importlib.resources
import importlib.util
import os
import sys
from types import ModuleType


site_module_path = ""
try:
    import progfigsite

    site_module_path = "progfigsite"
except ImportError:
    import progfiguration.example_site as progfigsite

    site_module_path = "progfiguration.example_site"


def set_site_module_filepath(filepath: str):
    """Use a Python package from a filepath as progfigsite

    This is intended to be called only once, at the beginning of program execution.

    Args:
        filepath: The path to the site package, eg "/path/to/my_progfigsite"
    """
    global site_module_path, progfigsite

    site_module_path = "set_site_module_path_progfigsite"

    # spec_from_file_location() will fail if the filepath is a directory,
    # but if the directory is a package, we can use its __init__.py file.
    if os.path.exists(f"{filepath}/__init__.py"):
        filepath = f"{filepath}/__init__.py"

    spec = importlib.util.spec_from_file_location(site_module_path, filepath)
    if spec is None:
        raise ImportError(f"Could not import site package from {filepath}")
    progfigsite = importlib.util.module_from_spec(spec)
    sys.modules[site_module_path] = progfigsite
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
        modpath = f"{site_module_path}.{submodule_path}"
    else:
        modpath = site_module_path
    return modpath


def site_submodule(submodule_path: str) -> ModuleType:
    """The Python module for a given site submodule

    Args:
        submodule_path: The path to the submodule, relative to the site package.
            This can be an empty string for the site package itself,
            or a dotted path to a submodule.
            E.g. "", "nodes", "nodes.example_node"
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
    """
    return importlib.resources.files(site_modpath(submodule_path)).joinpath(resource_name)
