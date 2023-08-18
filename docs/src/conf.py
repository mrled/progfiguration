# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Imports

import importlib.metadata
from pathlib import Path

# Paths

_project_root = Path(__file__).parent.parent.parent
_package_progfiguration = _project_root / "progfiguration"
_package_example_site = _project_root / "tests" / "data" / "simple" / "example_site"
_package_nnss_site = _project_root / "tests" / "data" / "nnss" / "nnss_progfigsite"


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = "progfiguration"
copyright = "2023, Micah R Ledbetter"
author = "Micah R Ledbetter"
version = importlib.metadata.version("progfiguration")
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    "sphinx.ext.intersphinx",
    # Autoapi generates docs for everything it can find in the source code.
    # (Sphinx's autodoc only generates docs for things that are explicitly imported in the docs.)
    "autoapi.extension",
    # Argparse autogeneration
    "sphinxarg.ext",
]

# TODO: make this work, it generates lot of spurious warnings at the moment.
# nitpicky = True

templates_path = ["_templates"]
exclude_patterns = [
    "*.egg-info",
    "*venv*",
    ".DS_Store",
    ".github",
    ".gitignore",
    "Thumbs.db",
    "dist",
    "_build",
]

# Link to other projects' documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Where autoapi finds the source code to document.
autoapi_dirs = [
    _package_progfiguration.as_posix(),
    _package_example_site.as_posix(),
    _package_nnss_site.as_posix(),
]

# By default autoapi documents imported members as if they are part of the module they're imported into.
# That's, dumb
autoapi_options = [
    "members",
    "private-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "undoc-members",
]


html_static_path = ["_static"]
templates_path = ["_templates"]

# Theme
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/mrled/progfiguration/",
    "source_branch": "master",
    "source_directory": "docs/src/",
}
