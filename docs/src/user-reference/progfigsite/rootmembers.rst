``progfigsite`` root members
============================

Sites must define a few members in their root package ``__init__.py``:


``site_name``
    a short user-facing string

``site_description``
    a longer user-facing string

``hoststore``
    An implementation of the :class:`progfiguration.inventory.invstores.HostStore` protocol.
    Progfiguration core ships with
    :class:`progfiguration.inventory.storeimpl.memhosts.MemoryHostStore`.

``secretstore``
    An implementation of the :class:`progfiguration.inventory.invstores.SecretStore` protocol.
    Progfiguration core ships with
    :class:`progfiguration.inventory.storeimpl.agesecrets.AgeSecretStore`

``mint_version()``
    a function that takes no arguments and returns a valid pip version number.

    This function should return a **new** version number,
    suitable for the next build of the pacakge.

    A simple implementation that uses the epoch time in the version number:

    .. code-block:: python

        def mint_version() -> str:
            from datetime import datetime

            dt = datetime.utcnow()
            epoch = int(dt.timestamp())
            version = f"1.0.{epoch}"
            return version

    Some implementations might instead pull the version number from an environment variable injected by a CI service, etc.

``get_version()``
    a function that takes no arguments and returns a valid pip version number.

    This function should return the **current** version number,
    for the currently-running package.

    It should first look for a ``builddata.version`` package with a string ``version`` member and return that.
    If that is not found, it should return a default version number.

    A reasonable implementation (for a progfig site package called ``example_site``):

    .. code-block:: python

        def get_version() -> str:
            try:
                from example_site.builddata import version
                return version.version
            except ImportError:
                return "0.0.1a0"

Progfiguration core ships with a convenience function
:meth:`progfiguration.inventory.storeimpl.invconf.inventory_conf`
which instantiates both a MemoryHostStore and an AgeSecretStore
based on an inventory config file.

Here is an exmple from :mod:`example_site`.

.. literalinclude:: ../../../../tests/data/simple/example_site/__init__.py
   :language: python
