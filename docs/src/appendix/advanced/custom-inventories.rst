Custom inventories
==================

An :ref:`progfigsite-concept-inventory`
is the storage for nodes, groups, secrets, etc for a site.

Any site can define their own inventory classes which implement
the :class:`progfiguration.inventory.invstores.HostStore` protocol
and the :class:`progfiguration.inventory.invstores.SecretStore` protocol.
