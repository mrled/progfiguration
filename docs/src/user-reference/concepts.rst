Important concepts
==================

.. _progfigsite-concept-core:

``progfiguration`` core
    The core pacakge containing generic code not specific to any site.

.. _progfigsite-concept-progfigsite:

Progfiguration sites (``progfigsite``\ s)
    A package containing all the code specific to a single site.

.. _progfigsite-concept-controller:

Controller
    This is the machine that contains a master Age key and can connect to all the nodes in the inventory.
    It can decrypt all secrets
    and can connect to all nodes via SSH when running the ``progfigsite deploy`` command.

.. _progfigsite-concept-inventory:

Inventory
    A :ref:`host store <progfigsite-concept-hoststore>` plus a :ref:`secret store <progfigsite-concept-secretstore>`.

.. _progfigsite-concept-hoststore:

Host store
    Where nodes, groups, and functions are defined.
    See :class:`progfiguration.inventory.invstores.HostStore`.

    Progfiguration ships with
    :class:`progfiguration.sitehelpers.memhosts.MemoryHostStore` which implements that protocol,
    and :meth:`progfiguration.sitehelpers.invconf.hosts_conf`
    which can instantiate one from a simple configuration file.

    Sites are free to instantiate a ``MemoryHostStore`` directly
    or implement their own ``HostStore``
    (in their :doc:`sitelib module </user-reference/progfigsite/sitelib>`)
    and use it instead.

.. _progfigsite-concept-secretstore:

Secret store
    How secrets are stored.
    See :class:`progfiguration.inventory.invstores.SecretStore`.

    Progfiguration ships with
    :class:`progfiguration.sitehelpers.agesecrets.AgeSecretStore` which implements that protocol,
    and :meth:`progfiguration.sitehelpers.invconf.secrets_conf`
    which can instantiate one from a simple configuration file.

    Sites are free to instantiate an ``AgeSecretStore`` directly
    or implement their own ``SecretStore``
    (in their :doc:`sitelib module </user-reference/progfigsite/sitelib>`)
    and use it instead.

.. _progfigsite-concept-node:

Node
    A machine to be configured.
    Must be defined in the inventory config file and have a Python module at ``progfigsite.nodes.NODENAME``.
    If the node has any secrets, they are stored as JSON files under ``progfigsite/nodes/NODENAME.secrets.json``.
    See :doc:`/user-reference/progfigsite/nodes`.

.. _progfigsite-concept-group:

Group
    Collections of nodes.
    Must be defined in the inventory config file and have a Python module at ``progfigsite.groups.GROUPNAME``.
    If the group has any secrets, they are stored as JSON files under ``progfigsite/groups/GROUPNAME.secrets.json``.
    See :doc:`/user-reference/progfigsite/groups`.

.. _progfigsite-concept-role:

Role
    Configuration code that can be applied to a node.
    A role might do something like install packages, set the contents of a configuration file, etc.
    These are Python modules at ``progfigsite.roles.ROLENAME``.
    Roles commonly contain data files to install on the node as well.
    See :doc:`/user-reference/progfigsite/roles`.

.. _progfigsite-concept-role-references:

Role reference
    Most role arguments are simple Python objects, like strings, ints, or :class:`pathlib.Path` objects.
    Role references are special arguments that are used to dynamically find argument values at runtime.
    Currently, progfiguration understands two kinds of references:
    :class:`progfiguration.inventory.roles.RoleCalculationReference`,
    which refers to the results of role calculations
    (see :doc:`/user-reference/progfigsite/roles` for more on calculations),
    and :class:`progfiguration.inventory.invstores.SecretReference`,
    which is a protocol that SecretStore backends must implement that refers to secret values.
    Role references are dereferenced at runtime.

.. _progfigsite-concept-function:

Function
    A function is a mapping of a node to a set of roles.
    Functions are defined inside the host store only --
    unlike groups and nodes, they don't have an object associated with them.

    A node can only have one function,
    but the function can map to multiple roles.
    When a node is provisioned, the roles associated with the function are applied to the node.
