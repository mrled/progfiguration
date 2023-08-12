How role arguments get applied
==============================

Roles may accept arguments.
When a role is applied to a node,
progfiguration looks up possible arguments in the following order:

1.  The default value for the argument, if one is provided by the role itself.
2.  The ``universal`` group.
3.  All other groups the node is a member of, in undetermined order.
    *Take care not to rely on the order of groups!*
    Defining the same argument in multiple groups is a footgun.
    TODO: Warn about this.
4.  The node itself.

Here's an example role:

.. code:: python

    # progfigsite.roles.example_role

    @dataclass(kw_only=True)
    class Role(ProgfigurationRole):

        username: str
        password: str

        # ...

A group could set the username:

.. code:: python

    # progfigsite.groups.universal

    group = Bunch(
        roles=Bunch(
            example_role={
                "username": "mr_the_plague",
            }
        ),
    )

And each node could set a separate password:

.. code:: python

    # progfigsite.nodes.the_gibson

    node = InventoryNode(
        # ...
        roles=Bunch(
            example_role={
                "password": "love-sex-secret-god",
            },
        ),
    )

Role result reference arguments
-------------------------------

Role arguments can reference data from the results of another role.
(Take care that role "results" may be requested before the role is applied,
see :doc:`/user-reference/progfigsite/roles`.)
You can set :class:`progfiguration.inventory.roles.RoleResultReference` role arguments
to retrieve the result of one role when passing an argument to another role.

.. code:: python

    node = InventoryNode(
        # ...
        roles=Bunch(
            example_role={
                "something": RoleResultReference("other_role", "result_field")
            },
        ),
    )

Secret reference arguments
--------------------------

You can also retrieve a secret from the encrypted secret store using
:class:`progfiguration.age.AgeSecretReference`.

.. code:: python

    node = InventoryNode(
        # ...
        roles=Bunch(
            example_role={
                "password": AgeSecretReference("secret_name")
            },
        ),
    )
