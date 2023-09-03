pyproject.toml edge cases
=========================

We found some edge cases and surprising behavior with pyproject.toml.

Dynamic version
---------------

We use

::

    [tool.setuptools.dynamic]
    version = {attr = "progfigsite.version.get_version"}

(Substitute your package name for ``progfigsite``.)

This looks in the :doc:`/user-reference/progfigsite/version`
for a function called ``get_version()``.
It runs that function

1.  when installing as editable via ``pip install -e '.'``, or
2.  when building the package with ``python -m build ...``
    (which is used under the hood when running ``progfiguration build ...``).

It finds this function inside the progfigsite package,
which means we must talk about package discovery.

Discoveries about package discovery
-----------------------------------

tl;dr: use `src-layout <https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout>`_
and everything will work implicitly.

src-layout is the path of least resistance when using pip editable installs
and package builds with setuptools.

::

    progfigsite_root_directory
    ├── pyproject.toml
    ├── ...
    └── src/
        └── progfigsite/
            ├── __init__.py
            ├── ...

With this layout, setuptools will find the ``progfigsite`` package automatically,
and will include all non-Python data files like ``inventory.conf`` (so-called "package data") implicitly.

Problems using flat layout
^^^^^^^^^^^^^^^^^^^^^^^^^^

Flat layout is similar to src-layout, but without the "src" directory.

::

    progfigsite_root_directory
    ├── pyproject.toml
    ├── ...
    └── progfigsite/
        ├── __init__.py
        ├── ...

We ran into problems with flat layout and do not recommend it for progfigsite packages.
Here are some very rough notes.

* We had to provide a ``[tool.setuptools.packages.find]`` section in ``pyproject.toml``,
  although I don't remember why
* When we did ``where = ["."]`` in that section,
  it seemed to work, but when trying to retrieve the version,
  it couldn't find the ``progfigsite`` module
  (``ModuleNotFoundError: No module named 'progfigsite'``).
* We had to do ``where = ["progfigsite"]`` to get it to find the ``progfigsite`` module.
* We also had trouble with package data,
  where non-Python files like secrets JSON files or ``inventory.conf`` files
  would not get included in packages built by setuptools.
