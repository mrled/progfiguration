``progfigsite`` root members
============================

A site's root ``__init__.py`` must contain the following:

``site_name``
    The name of the Python package, e.g. ``example_site``. Must match the name of the package in ``pyproject.toml``.

``site_description``
    A longer user-facing string.

``get_version()``
    A function that takes no arguments and returns a valid pip version number.

    This function should return the **current** version number,
    for the currently-running package.
    (This is different from the ``mint_version()`` function
    in :doc:`/user-reference/progfigsite/inventory`,
    which returns the **next** version number for a new build.)

    It should first look for a ``builddata.version`` package with a string ``version`` member and return that.
    If that is not found, it should return a default version number.

Here is an example root ``__init__.py`` file from :mod:`example_site`.

.. literalinclude:: ../../../../tests/data/simple/example_site/__init__.py
   :language: python
