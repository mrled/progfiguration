from progfiguration.inventory.nodes import InventoryNode
from progfiguration.progfigtypes import Bunch

node = InventoryNode(
    address="node1.example.com",
    user="root",
    notes="",
    age_pubkey="",
    ssh_host_fingerprint="",
    psy0mac="",
    serial="",
    roles=Bunch(
        settz={
            "timezone": "UTC",
        },
    ),
)
