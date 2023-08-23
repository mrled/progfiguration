``progfigsite`` ``inventory.conf`` File
=======================================

An ``inventory.conf`` file is not technically part of progfiguration core,
but it can be used with
:func:`progfiguration.sitehelpers.invconf.hosts_conf` and
:func:`progfiguration.sitehelpers.invconf.secrets_conf` to create a
:ref:`host store <progfigsite-concept-hoststore>` and
:ref:`secrets store <progfigsite-concept-secretsstore>` respectively.

Here's an example from :mod:`example_site`:

.. literalinclude:: ../../../../tests/data/simple/example_site/inventory.conf
    :language: ini

By itself, that inventory file does nothing,
but when referenced in the site's root module
it generates the host and secret stores.
Here is the root module from :mod:`example_site`:

.. literalinclude:: ../../../../tests/data/simple/example_site/__init__.py
    :language: python
