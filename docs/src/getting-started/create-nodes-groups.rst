Creating your first node
========================

Nodes are the individual hosts in your site.

In :doc:`/getting-started/new-site`,
the ``progfiguration newsite`` command created an example node called ``node1.py``.
It looks like this:

.. literalinclude:: ../../../progfiguration/newsite/exnode.py

Create a separate Python module for each node in your site.
We'll use this example node in this tutorial.

Encrypting secrets for nodes
----------------------------

One thing that ``progfiguration newsite`` does not do is create Age keys for each node,
which allows us to store encrypted secrets for the node.
For each node:

1.  Create a key with ``age-keygen``.
    It's probably best to do this on each individual node,
    but easier to do it for all nodes in a script on your controller.
2.  Copy the public key into the node's Python module,
    like this:

    .. code:: python

        node = InventoryNode(
            address="agassiz.home.micahrl.com",
            user="root",
            sitedata=dict(
                age_pubkey="age17wp408dyw8s4tszh230t92k4gyeeq3se48sx7yjkpmempja6xvgqnamqp3",
            ),
            # ...
        )

3.  Place the private key in the correct location on each node,
    by default ``/etc/progfiguration/node.age``.

.. note:: What is ``sitedata``?

    Progfiguration supports pluggable secrets storage backends that implement
    the :class:`progfiguration.inventory.invstores.SecretStore` protocol.
    The ``newsite`` command uses a build-in backend that uses Age,
    :class:`progfiguration.inventory.storeimpl.agesecrets.AgeSecretStore`,
    but you could also write your own and use that instead.
    Because Age-related information is site-specific,
    it goes in the ``.sitedata`` attribute of a node object.

Once we have the pubkey stored in the node's Python module,
you can use ``progfigsite encrypt`` to store secrets.

Creating groups
---------------

Groups are collections of nodes,
designed to allow you to specify common configurations one time.
The ``progfiguration newsite`` command created an example group:

.. literalinclude:: ../../../progfiguration/newsite/exgroup.py

Groups can also have secrets,
but there is no group age key.
When encrypting secrets for a group with ``progfigsite encrypt --group group1 ...``,
the secret is just encrypted for all of the nodes individually.

(This means that adding a new group member requires re-encrypting all secrets.
In the future, the tooling will make this easier,
but for now this is a manual process.)

Add nodes and groups to the inventory
-------------------------------------

All nodes and groups you create must be listed in the inventory file,
or progfiguration will not be able to find them.
We'll explore the inventory in :doc:`/getting-started/create-role`.
