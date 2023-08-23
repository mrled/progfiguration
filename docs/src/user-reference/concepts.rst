Important concepts
==================

.. _progfigsite-concept-core:

``progfiguration`` core
    The core pacakge containing generic code not specific to any site.

.. _progfigsite-concept-progfigsite:

Progfiguration sites (``progfigsite``\ s)
    A package containing all the code specific to a single site.

.. _progfigsite-concept-controller:

The controller
    This is the machine that contains a master Age key and can connect to all the nodes in the inventory.

.. _progfigsite-concept-inventory:

Inventory
    Storage for nodes, groups, functions, roles, and secrets for a progfigsite.
    Made up of an implementation of the :class:`progfiguration.inventory.invstores.HostStore` protocol
    plus an implementation of the :class:`progfiguration.inventory.invstores.SecretStore` protocol.

    Progfiguration ships with
    :class:`progfiguration.sitehelpers.memhosts.MemoryHostStore` and
    :class:`progfiguration.sitehelpers.agesecrets.AgeSecretStore`
    which implement those two protocols, as well as convenience functions
    :meth:`progfiguration.sitehelpers.invconf.hosts_conf` and
    :meth:`progfiguration.sitehelpers.invconf.secrets_conf`
    which can instantiate one of each based on a simple configuration file.

    Sites may also implement their own implementation of HostStore and/or SecreStore
    (in their own :doc:`sitelib module </user-reference/progfigsite/sitelib>`)
    and use those instead.

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
    Functions are defined inside the inventory config file only
    (and do not have a Python module associated with them).
    A node can only have one function.
