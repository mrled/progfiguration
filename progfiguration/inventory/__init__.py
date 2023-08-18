"""The progfiguration inventory

    An inventory is the heart of a progfigsite.
    It's composed of the following:

    * `progfiguration.inventory.nodes.InventoryNode`: A machine that can be configured.
      See an example node definition in `example_site.nodes.node1`.
    * Group: Simple collections of nodes, which can provide shared configuration.
      See an example group definition in `example_site.groups.group1`.
    * Function: Simple collection of nodes, which have a list of roles to be applied.
      Functions can't share any configuration,
      so they don't have a source code file of their own.
      They're just defined in the inventory configuration file.
    * `progfiguration.inventory.roles.ProgfigurationRole`: A configuration that can be applied to a function.
      See an example role in `example_site.roles.settz`.

    The best way to understand the inventory is to look at an example inventory configuration file.
    Here's the inventory configuration file for `example_site`:

    ```ini
    .. include:: ../../tests/data/simple/example_site/inventory.conf
    ```
"""
