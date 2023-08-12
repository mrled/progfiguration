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

*   See also: :doc:`/user-reference/role-arguments`.
*   In the :doc:`/user-reference/progfigsite/inventory`,
    roles are assigned to functions, and functions are assigned to nodes.
*   They *must* be annotated with ``@dataclass(kw_only=True)``
*   Dataclass fields are arguments to the role,
    which may be defined on nodes and/or groups.
*   The ``apply()`` function contains the logic for applying the role to a node.
    It can reference fields.
*   An optional ``results()`` function can be defined to return a dict of values.
    **This ``results()`` function cannot rely on ``apply()`` having been called.**
    Yes, arguably this is a bad name.

.. note:: The design of the ``results()`` function.

    This function should return *easy to calculate* values. This is a
    judgement call, but note that other roles may reference the results
    multiple times.

    In the design of this API, I considered allowing ``apply()`` to return
    results directly, and possibly caching them for later use. The
    complexity of that design caused me to reject it, at least for now.
    Instead, the ``results()`` design has some tradeoffs, like needing to
    factor out code that is shared by ``apply()`` and ``results()``, and no
    ability to cache. However, in exchange, the implementation is simpler.

Example ``.results()`` methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All ``results()`` methods should be idempotent,
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

        def results(self):
            return {
                # Homedir is returned in results():
                "homedir": self.homedir,
            }

And instead do something like:

1.  Decide not to return the homedir in ``results()`` at all.
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

            def results(self):
                return {
                    # The homedir is defined statically so it can be returned in results()
                    "homedir": self.homedir,
                }
