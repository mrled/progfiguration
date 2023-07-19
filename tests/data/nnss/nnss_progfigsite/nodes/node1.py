from progfiguration.inventory.nodes import InventoryNode
from progfiguration.progfigtypes import Bunch

node = InventoryNode(
    address="node1.example.mil",
    flavortext="This is an example in the Nevada National Security Site (NNSS) progfigsite",
    user="root",
    notes="",
    age_pubkey="",
    ssh_host_fingerprint="",
    psy0mac="",
    serial="",
    roles=Bunch(
        settz={
            "timezone": "US/Pacific",
        },
    ),
)
