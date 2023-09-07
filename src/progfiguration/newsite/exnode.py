"""Example node"""

from progfiguration.inventory.nodes import InventoryNode

node = InventoryNode(
    address="node1.example.com",
    user="root",
    ssh_host_fingerprint="",
    roles=dict(
        settz={
            "timezone": "UTC",
        },
    ),
)
