``progfigsite.version`` module
==============================

Only one item is required in this module: ``get_version()``.

``get_version()``
    A function that takes no arguments and returns a valid pip version number.

    This function should return the **current** version number,
    for the currently-running package.
    (This is different from the ``mint_version()`` function
    in :ref:`/user-reference/progfigsite/inventory`,
    which returns the **next** version number for a new build.)

    It should first look for a ``builddata.version`` package with a string ``version`` member and return that.
    If that is not found, it should return a default version number.


Here is an example root ``version.py`` file from :mod:`example_site`.

.. literalinclude:: ../../../../tests/data/simple/example_site/version.py
   :language: python
