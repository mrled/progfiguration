Creating your first role
========================

Roles are generic, composable objects with a ``.apply()`` method
which configure your nodes.
Conceptually, if you are familiar with Ansible's roles,
you will be comfortable with progfiguration's roles.

In :doc:`/getting-started/new-site`,
the ``progfiguration newsite`` command created an example role called ``role1.py``.
It looks like this:

.. literalinclude:: ../../../src/progfiguration/newsite/exrole.py

This role takes one argument, a string timezone name,
and sets the node's timezone.
Nodes and groups provide the time zone name via role arguments.
You can see the example group we created provides a timezone:

.. literalinclude:: ../../../src/progfiguration/newsite/exgroup.py

Adding a role to the inventory
------------------------------

Like nodes and groups, roles must also be added to the inventory.
In order for a role to be applied to a node,
the role and the node must be connected via a :ref:`function <progfigsite-concept-function>`.

1.  The **role** must be part of a function in the ``function_role_map``.
    One role might belong to several functions,
    or it might only be used in one.
2.  The **node** must be assigned that function in ``node_function_map``.
    Nodes are assigned exactly one function.

Here's a simple inventory demonstrating this.
For the nodes to have roles applied to them,
we need a function for each type of machine, like ``webserver`` and ``dbserver``.
Each function can then apply whatever roles it likes.

.. code:: ini

    [secrets]
    controller_age_path = /path/to/controller.age
    controller_age_pub = ...
    node_fallback_age_path = /etc/progfiguration/node.age

    [groups]
    group1 = node1

    [node_function_map]
    web1 = webservers
    web2 = webservers
    db1 = dbservers

    [function_role_map]
    webservers =
        basic_config
        nginx_base
        nginx_yourapp
    dbservers =
        basic_config
        postgres


Role references and secrets
---------------------------

Not found in our site created by ``progfiguration newsite``
are :ref:`role references <progfigsite-concept-role-references>`,
which are special arguments that are dereferenced at runtime.
We use role references,
specifically :class:`progfiguration.age.AgeSecretReference` objects,
to decrypt secrets for a role.
We'll create one now.

See :doc:`/user-reference/progfigsite/roles` for more details on how roles work,
and a discussion of role calculations.

Here, we will add an example role that accepts a password.
The role creates a service account and then sets a password for it.

.. code:: python

    """Create a service account"""

    from dataclasses import dataclass
    import shutil

    from progfiguration.cmd import magicrun
    from progfiguration.inventory.roles import ProgfigurationRole


    @dataclass(kw_only=True)
    class Role(ProgfigurationRole):
        """Set the timezone on an Alpine Linux host."""

        username: str
        primgroup: str
        password: str

        def apply(self):
            magicrun(["adduser", "-D", "-S", "-s", "/bin/sh", "-G", self.primgroup, self.username]
            magicrun(["chpasswd"], input=f"{self.username}:{self.password}")

You could set the username and password like this in a role:

.. code:: python

    """Example node"""

    from progfiguration.age import AgeSecretReference
    from progfiguration.inventory.nodes import InventoryNode

    node = InventoryNode(
        address="node1.example.com",
        ssh_host_fingerprint="...",
        roles=dict(
            create_service_account={
                "username": "testuser",
                "password": "p@ssw0rd!",
            },
        ),
    )

... but this has the downside of storing the password in plain text.
Instead, we can encrypt our secrets with Age.
Using the Age key for the nodes we created in :doc:`/getting-started/create-nodes-groups`,
we can run:

.. code:: shell

    progfigsite encrypt --node node1 --value "p@ssw0rd!" --save-as service_account_password

This will encrypt the secret with Age and
store the results in ``progfigsite/nodes/node1.secrets.json``,
creating that file if it doesn't exist.

Encrypting secrets with ``progfigsite encrypt`` will always include the controller's public key
(found in the ``inventory.conf``) in the list of recipients,
meaning that the controller will be able to see all secret values.

Now that we have an encrypted password,
we can use a role argument reference to have it decrypted at runtime.

.. code:: python

    node = InventoryNode(
        address="node1.example.com",
        # ...
        roles=dict(
            create_service_account={
                "username": "testuser",
                "password": AgeSecretReference("service_account_password"),
            },
        ),
    )
