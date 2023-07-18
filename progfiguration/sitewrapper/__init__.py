"""Progfiguration site wrapper

If the user site exists, import it.
Otherwise, import the example site.

Provide functions for retrieving site-specific resources,
including submodules and data files.
(importlib.import_module() can be used to import a module from a string,
but it requires the full module path.
Even though we 'import X as site' here,
'site' is not a module name that import_module() can use.)

Site packages must contain the following submodules:
- nodes
- roles
- groups

And the following variables:
- package_inventory_file

And may contain an optional 'sitelib' submodule.
This is not used by progfiguration, but can be used internally in the site package.

Other names are reserved for future use by progfiguration.
"""

import importlib
from importlib.resources import files as importlib_resources_files
from types import ModuleType


site = None
site_module_path = ""
try:
    import progfigsite as site
    site_module_path = "progfigsite"
except ImportError:
    import progfiguration.example_site as site
    site_module_path = "progfiguration.example_site"


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
    return importlib_resources_files(site_modpath(submodule_path)).joinpath(resource_name)
