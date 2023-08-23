``progfigsite`` root members
============================

A site's root ``__init__.py`` must contain the following definitions and function calls:


``site_name``
    The name of the Python package, e.g. ``example_site``. Must match the name of the package in ``pyproject.toml``.

``sitewrapper.set_progfigsite_by_module_name(site_name)``
    After setting the site name, you must call this function to tell progfiguration core the name of the package.
    This must happen in the root module, and before any progfiguration core functions are called.

``site_description``
    A longer user-facing string.

``hoststore``
    An implementation of the :class:`progfiguration.inventory.invstores.HostStore` protocol.
    Progfiguration core ships with
    :class:`progfiguration.sitehelpers.memhosts.MemoryHostStore`,
    and sites are free to implement their own.

``secretstore``
    An implementation of the :class:`progfiguration.inventory.invstores.SecretStore` protocol.
    Progfiguration core ships with
    :class:`progfiguration.sitehelpers.agesecrets.AgeSecretStore`,
    and sites are free to implement their own.

``mint_version()``
    A function that takes no arguments and returns a valid pip version number.

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
    A function that takes no arguments and returns a valid pip version number.

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
:meth:`progfiguration.sitehelpers.invconf.inventory_conf`
which instantiates both a MemoryHostStore and an AgeSecretStore
based on an inventory config file.

Here is an exmple from :mod:`example_site`.

.. literalinclude:: ../../../../tests/data/simple/example_site/__init__.py
   :language: python
