``progfigsite.nodes`` Module
============================

This module should contain a separate Python file for each host.
For instance:

.. code-block:: text

    progfigsite/
        __init__.py
        ...
        nodes/
            __init__.py
            host1.py
            host2.py
            host3.py

Node files
----------

Each node file should contain a class named ``node`` that inherits from
:class:`progfiguration.inventory.nodes.InventoryNode`.

For instance, the node defined in :mod:`example_site.nodes.node1`:

.. literalinclude:: ../../../../tests/data/simple/example_site/nodes/node1.py
   :language: python

Node secret files with AgeSecretStore
-------------------------------------

.. note:: Information in this section only applies to AgeSecretStore

    This section only applies to sites that use the
    :class:`progfiguration.inventory.storeimpl.agesecrets.AgeSecretStore`
    secret storage implementation.
    It's what ships with progfiguration core so it's the easiest to get started with,
    but other secret storage backends will work differently.

If a node has secrets encrypted with ``progfiguration encrypt``,
they will be stored in a file named ``<node name>.secrets.json``
in the ``nodes`` package.
