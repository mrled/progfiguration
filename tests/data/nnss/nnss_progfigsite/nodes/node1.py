from pathlib import Path

from progfiguration.inventory.nodes import InventoryNode

node = InventoryNode(
    address="node1.example.mil",
    user="root",
    ssh_host_fingerprint="",
    sitedata=dict(
        # Find the age key in the nnss project directory.
        # Normally you would not want to keep it here,
        # as it would mean your node key is in version control.
        age_key_path=(Path(__file__).parent.parent.parent / "node1.age").as_posix(),
        age_pubkey="age1g6gf04flzm0tk64nztfxklystvaymeznfsts56t5rs2mtrvsqg6qhyn60n",
    ),
    roles=dict(
        settz={
            "timezone": "US/Pacific",
        },
    ),
)
