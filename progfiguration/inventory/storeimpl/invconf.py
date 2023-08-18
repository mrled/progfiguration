"""An inventory configuration file that uses AgeSecretStore and MemoryHostStore"""

from configparser import ConfigParser
from pathlib import Path
from typing import Tuple, Union

from progfiguration.inventory.storeimpl.agesecrets import AgeSecretFileStore
from progfiguration.inventory.storeimpl.memhosts import MemoryHostStore


def inventory_conf(cfgfile: Union[Path, ConfigParser]) -> Tuple[MemoryHostStore, AgeSecretFileStore]:
    """Read the inventory configuration file and return the inventory and secret store"""

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

    secretstore = AgeSecretFileStore(
        controller_age_pubkey=config.get("general", "controller_age_pub"),
        decryption_age_privkey_path_list=[
            config.get("general", "controller_age_path"),
            config.get("general", "node_fallback_age_path"),
        ],
    )

    return hoststore, secretstore
