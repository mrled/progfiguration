# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Imports

from pathlib import Path


# Paths

_project_root = Path(__file__).parent.parent
_package_progfiguration = _project_root / "progfiguration"
_package_example_site = _project_root / "tests" / "data" / "simple" / "example_site"


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = "progfiguration"
copyright = "2023, Micah R Ledbetter"
author = "Micah R Ledbetter"
release = "0.0.2a3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    # Autoapi generates docs for everything it can find in the source code.
    # (Sphinx's autodoc only generates docs for things that are explicitly imported in the docs.)
    "autoapi.extension",
    # Markdown support
    "myst_parser",
]


templates_path = ["_templates"]
exclude_patterns = [".gitignore", "_build", "Thumbs.db", ".DS_Store"]

# Where autoapi finds the source code to document.
autoapi_dirs = [_package_progfiguration.as_posix(), _package_example_site.as_posix()]


html_static_path = ["_static"]

html_theme = "furo"
