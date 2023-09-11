pyproject.toml edge cases
=========================

We found some edge cases and surprising behavior with pyproject.toml.

Default ``pyproject.toml``
--------------------------

When creating a new site with ``progfiguration newsite ...``,
it creates a ``pyproject.toml`` for you that looks like the following.
(Substitute a site name like ``mysite`` for ``{$}name``,
and some reasonable description like ``the example.org site`` for ``{$}descriptiono``.)

..  literalinclude:: ../../../src/progfiguration/newsite/pyproject.toml.temple
    :language: toml

Dynamic version
---------------

We use

::

    [tool.setuptools.dynamic]
    version = {attr = "SITENAME.get_version"}

This looks in the root module for a function called ``get_version()``.
It runs that function

1.  when installing as editable via ``pip install -e '.'``, or
2.  when building the package with ``python -m build ...``
    (which is used under the hood when running ``progfiguration build ...``).

It finds this function inside the SITENAME package,
which means we must talk about package discovery.

Discoveries about package discovery
-----------------------------------

tl;dr: use `src-layout <https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout>`_
and everything will work easily.

src-layout is the path of least resistance when using pip editable installs
and package builds with setuptools.

::

    progfigsite_root_directory
    ├── pyproject.toml
    ├── ...
    └── src/
        └── SITENAME/
            ├── __init__.py
            ├── ...

With this layout, setuptools will find the ``SITENAME`` package automatically,
and will include all non-Python data files like ``inventory.conf``
(so-called "package data") via our ``[tool.setuptools.package-data]`` section.

Problems using flat layout
^^^^^^^^^^^^^^^^^^^^^^^^^^

Flat layout is similar to src-layout, but without the "src" directory.

::

    progfigsite_root_directory
    ├── pyproject.toml
    ├── ...
    └── SITENAME/
        ├── __init__.py
        ├── ...

We ran into problems with flat layout and do not recommend it for progfigsite packages.
Here are some very rough notes.

* We had to provide a ``[tool.setuptools.packages.find]`` section in ``pyproject.toml``.
* When we did ``where = ["."]`` in that section,
  it seemed to work, but when trying to retrieve the version,
  it couldn't find the ``SITENAME`` module
  (``ModuleNotFoundError: No module named 'SITENAME'``).
* We had to do ``where = ["SITENAME"]`` to get it to find the ``SITENAME`` module.
* We also had trouble with package data,
  where non-Python files like secrets JSON files or ``inventory.conf`` files
  would not get included in packages built by setuptools.
  In the ``[tool.setuptools.package-data]`` section,
  we tried both ``SITENAME = ["*"]`` and ``"*" = ["*"]`` with no success.
