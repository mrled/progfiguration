"""An inventory configuration file that uses AgeSecretStore and MemoryHostStore"""

from configparser import ConfigParser
from pathlib import Path
from typing import Tuple, Union

from progfiguration.inventory.storeimpl.agesecrets import AgeSecretStore
from progfiguration.inventory.storeimpl.memhosts import MemoryHostStore


def inventory_conf(cfgfile: Union[Path, ConfigParser]) -> Tuple[MemoryHostStore, AgeSecretStore]:
    """Read the inventory configuration file and return the inventory and secret store

    An example inventory file:

    .. code-block:: ini

        [general]
        # The controller has an age key which can be used to decrypt any secret.
        # When this file is not present, progfiguration will still work,
        # but activities that require the secret key will throw errors.
        controller_age_path = /path/to/controller.age

        # We must hard code the public key in this file as well,
        # so that it is available even when we aren't running on the controller.
        controller_age_pub = paste the public key here

        # The default/fallback location for the age key on each node.
        node_fallback_age_path = /path/to/node.age

        ####
        # Assign group membership
        # You can specify more than one group by separating items with newlines or spaces
        [groups]
        group1 = node1
        # group2 = node1 node2 node3

        ####
        # Assign each node to a function.
        # WARNING: Any node not listed here will not be visible to progfiguration,
        # meaning that it cannot be deployed to, will not be in the 'universal' group, etc.
        [node_function_map]
        node1 = func1

        ####
        # Set the list of roles for each function
        # Roles can be separated by newlines or spaces
        [function_role_map]
        func1 = settz
        # func2 = settz otherrole asdf etc
    """

    if isinstance(cfgfile, ConfigParser):
        config = cfgfile
    else:
        config = ConfigParser()
        with cfgfile.open() as f:
            config.read_file(f)

    hoststore = MemoryHostStore(
        groups={g: m.split() for g, m in config.items("groups")},
        node_function_map={n: f for n, f in config.items("node_function_map")},
        function_role_map={f: r.split() for f, r in config.items("function_role_map")},
    )

    secretstore = AgeSecretStore(
        controller_age_pubkey=config.get("general", "controller_age_pub"),
        decryption_age_privkey_path_list=[
            config.get("general", "controller_age_path"),
            config.get("general", "node_fallback_age_path"),
        ],
    )

    return hoststore, secretstore
