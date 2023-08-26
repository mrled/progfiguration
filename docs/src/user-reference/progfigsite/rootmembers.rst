``progfigsite`` root members
============================

A site's root ``__init__.py`` must contain the following definitions and function calls:


``site_name``
    The name of the Python package, e.g. ``example_site``. Must match the name of the package in ``pyproject.toml``.

``sitewrapper.set_progfigsite_by_module_name(site_name)``
    After setting the site name, you must call this function to tell progfiguration core the name of the package.
    This must happen in the root module, and before any progfiguration core functions are called.
    See also :meth:`progfiguration.sitewrapper.set_progfigsite_by_module_name`.

``site_description``
    A longer user-facing string.

``hoststore``
    An implementation of the :class:`progfiguration.inventory.invstores.HostStore` protocol.
    Progfiguration core ships with
    :class:`progfiguration.sitehelpers.memhosts.MemoryHostStore`
    which can be instantiated directly,
    or via :meth:`progfiguration.sitehelpers.invconf.hosts_conf` and a configuration file.
    Sites are free to implement their own alternative.

``secretstore``
    An implementation of the :class:`progfiguration.inventory.invstores.SecretStore` protocol.
    Progfiguration core ships with
    :class:`progfiguration.sitehelpers.agesecrets.AgeSecretStore`,
    which can be instantiated directly,
    or via :meth:`progfiguration.sitehelpers.invconf.secrets_conf` and a configuration file.
    Sites are free to implement their own alternative.

``mint_version()``
    A function that takes no arguments and returns a valid pip version number.

    This function should return a **new** version number,
    suitable for the next build of the pacakge.
    (This is different from the ``get_version()`` function in :ref:`/user-reference/progfigsite/version`,
    which returns the **current** version number.)

    Progfiguration core ships with
    :func:`progfiguration.sitehelpers.siteversion.mint_version_factory_from_epoch`,
    which will return a function that uses the epoch time in the version number.
    Some implementations might prefer to implement their own ``mint_version()``,
    perhaps to pull the version number from an environment variable injected by a CI service, etc.

Here is an example root ``__init__.py`` file from :mod:`example_site`.

.. literalinclude:: ../../../../tests/data/simple/example_site/__init__.py
   :language: python
