``progfigsite.roles`` Module
============================

This module should contain a separate module for each role.
Simple roles may be single-file modules;
more complex roles or roles with included data files can be packages.
For instance:

.. code-block:: text

    progfigsite/
        __init__.py
        ...
        roles/
            __init__.py
            role1.py
            role2/
                __init__.py
                datafile.txt
                ...
            ...

Role packages
-------------

Each role module should contain a subclass of :class:`progfiguration.inventory.roles.ProgfigurationRole`
with the name ``Role``,
and annotated with ``@dataclass(kw_only=True)``

For instance, the node defined in :mod:`example_site.roles.settz`,
which set's a node's timezone:

.. literalinclude:: ../../../../tests/data/simple/example_site/roles/settz.py
    :language: python

Some things worth noting about roles:

*   In the :doc:`/user-reference/progfigsite/inventory`,
    roles are assigned to functions, and functions are assigned to nodes.
*   They *must* be annotated with ``@dataclass(kw_only=True)``
*   Dataclass fields are arguments to the role,
    which may be defined on nodes and/or groups.
*   The ``apply()`` function contains the logic for applying the role to a node.
    It can reference fields.
*   An optional ``calculations()`` function can be defined to return a dict of values.
    These values are available to other roles as role calculation references.
    **The calculations() function cannot rely on apply() having been called.**

.. note:: The design of the ``calculations()`` function.

    This function should return *easy to calculate* values.
    This is a judgement call,
    but note that other roles may reference the calculations multiple times.

    In the design of this API,
    we considered allowing ``apply()`` to return results directly,
    but the complexity was reason to reject it.
    Instead, the ``calculations()`` design has some tradeoffs,
    like needing to factor out code that is shared by ``apply()`` and ``calculations()``,
    and no ability to cache.
    However, in exchange, the implementation is simpler.

Writing roles
-------------

Progfiguration core has some functionality designed to make it easier to write roles.

*   :mod:`progfiguration.localhost`
    has some helper functions for interacting with the local system,
    like :func:`progfiguration.localhost.LocalhostLinux.cp` for copying a file.
*   It provides :func:`progfiguration.localhost.LocalhostLinux.temple` for a simple string template.
    This is not as advanced as full templating engines like ``jinja2``,
    as it just provides very simple token replacement,
    but it is sufficient for simple tasks.

These helpers are supposed to be very simple and limited in scope.
Users are encouraged to write their own helpers inside :doc:`/user-reference/progfigsite/sitelib`.

Role calculations
-----------------

All ``calculations()`` methods should be idempotent,
and should not rely on ``apply()`` having been called.
This means that you must **avoid** doing something like this:

.. code:: python

    @dataclass(kw_only=True)
    class Role(ProgfigurationRole):

        username: str

        # Homedir is calculated based on state of the system --
        # this will fail before the user is created.
        @property
        def homedir(self):
            return self.localhost.users.getent_user(self.username).homedir

        def apply(self):
            self.localhost.users.add_service_account(self.username, self.username, home=True)

        def calculations(self):
            return {
                # Homedir is returned in calculations():
                "homedir": self.homedir,
            }

And instead do something like:

1.  Decide not to return the homedir in ``calculations()`` at all.
    Instead, you might return the username,
    and let the caller look up the homedir if they need it.

2.  Define the homedir as a static path and pass it as an argument to ``add_service_account()``:

    .. code:: python

        @dataclass(kw_only=True)
        class Role(ProgfigurationRole):

            username: str

            # It is safe to refer to self.username, which is passed in when the Role class is instantiated
            @property
            def homedir(self):
                return Path(f"/home/{self.username}")

            def apply(self):
                # Rather than `home=True`, which creates the homedir in the default location,
                # we pass the homedir location directly.
                self.localhost.users.add_service_account(self.username, self.username, home=self.homedir)

            def calculations(self):
                return {
                    # The homedir is defined statically so it can be returned in calculations()
                    "homedir": self.homedir,
                }


Role arguments
--------------

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

    group = dict(
        roles=dict(
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
        roles=dict(
            example_role={
                "password": "love-sex-secret-god",
            },
        ),
    )

Role calculation reference arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Role arguments can reference data from the calculations of another role.
(Take care that role calculations may be requested before the role is applied,
see :doc:`/user-reference/progfigsite/roles`.)
You can set :class:`progfiguration.inventory.roles.RoleCalculationReference` role arguments
to retrieve a calculation from one role when passing an argument to another role.

.. code:: python

    node = InventoryNode(
        # ...
        roles=dict(
            example_role={
                "something": RoleCalculationReference("other_role", "calculation_name")
            },
        ),
    )

Secret reference arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also retrieve a secret from the encrypted secret store using
:class:`progfiguration.age.AgeSecretReference`.

.. code:: python

    node = InventoryNode(
        # ...
        roles=dict(
            example_role={
                "password": AgeSecretReference("secret_name")
            },
        ),
    )
