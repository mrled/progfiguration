``progfigsite`` root members
============================

A site's root ``__init__.py`` must contain the following:

``site_name``
    The name of the Python package, e.g. ``example_site``. Must match the name of the package in ``pyproject.toml``.

``site_description``
    A longer user-facing string.

Here is an example root ``__init__.py`` file from :mod:`example_site`.

.. literalinclude:: ../../../../tests/data/simple/example_site/__init__.py
   :language: python
