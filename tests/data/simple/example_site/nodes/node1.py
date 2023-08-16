from progfiguration.inventory.nodes import InventoryNode

node = InventoryNode(
    address="node1.example.com",
    user="root",
    age_pubkey="",
    ssh_host_fingerprint="",
    roles=dict(
        settz={
            "timezone": "UTC",
        },
    ),
)
