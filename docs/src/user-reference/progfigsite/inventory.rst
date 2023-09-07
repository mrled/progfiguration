``progfigsite`` inventory module
================================

Required attributes and function calls


``sitewrapper.set_progfigsite_by_module_name(site_name)``
    You must call this function to tell progfiguration core the name of the package.
    This must happen before any progfiguration core functions are called.
    See also :meth:`progfiguration.sitewrapper.set_progfigsite_by_module_name`.

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
    (This is different from the ``get_version()`` function in :doc:`/user-reference/progfigsite/version`,
    which returns the **current** version number.)

    Progfiguration core ships with
    :func:`progfiguration.sitehelpers.siteversion.mint_version_factory_from_epoch`,
    which will return a function that uses the epoch time in the version number.
    Some implementations might prefer to implement their own ``mint_version()``,
    perhaps to pull the version number from an environment variable injected by a CI service, etc.


``progfigsite`` ``inventory.conf`` File
---------------------------------------

An ``inventory.conf`` file is not technically part of progfiguration core,
but it can be used with
:func:`progfiguration.sitehelpers.invconf.hosts_conf` and
:func:`progfiguration.sitehelpers.invconf.secrets_conf` to create a
:ref:`host store <progfigsite-concept-hoststore>` and
:ref:`secrets store <progfigsite-concept-secretstore>` respectively.

Here's an example from :mod:`example_site`:

.. literalinclude:: ../../../../tests/data/simple/example_site/inventory.conf
    :language: ini

By itself, that inventory file does nothing,
but when referenced in the site's inventory module
it generates the host and secret stores.
Here is the inventory module from :mod:`example_site`:

.. literalinclude:: ../../../../tests/data/simple/example_site/inventory.py
    :language: python

Inventory without ``inventory.conf``
------------------------------------

As noted, you can instantiate the ``HostStore`` and ``SecretStore`` classes yourself,
as in this example.

.. literalinclude:: ../../../../tests/data/nnss/nnss_progfigsite/inventory.py
    :language: python
