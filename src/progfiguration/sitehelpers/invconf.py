"""Inventory configuration files that can be used with AgeSecretStore and MemoryHostStore"""

from configparser import ConfigParser
from pathlib import Path
import sys
from typing import Union

from progfiguration import sitewrapper
from progfiguration.sitehelpers.agesecrets import AgeSecretStore
from progfiguration.sitehelpers.memhosts import MemoryHostStore


CfgfileArgument = Union[Path, str, ConfigParser]


def _parse_cfgfile_argument(cfg: CfgfileArgument) -> ConfigParser:
    """Parse a cfgfile argument into a Path and a ConfigParser

    Arguments:

    ``cfgfile``:
        The path to the config file, or a ConfigParser object.
        If a ConfigParser, it is used directly.
        If a relative path, it look relative to the progfigsite package root,
        then relative to the current working directory.
    """
    if isinstance(cfg, ConfigParser):
        return cfg
    cfg_path = Path(cfg) if isinstance(cfg, str) else cfg
    if not cfg_path.is_absolute():
        submodule_cfgpath = sitewrapper.site_submodule_resource("", cfg_path.as_posix())
        print(f"Trying relative submodule_cfgpath {submodule_cfgpath}", file=sys.stderr)
        if submodule_cfgpath.is_file():  # Traversable doesn't have .exists()
            print(f"Using relative submodule_cfgpath {submodule_cfgpath}", file=sys.stderr)
            cfg_path = submodule_cfgpath
        else:
            print(f"Using relative cfg_path {cfg_path}", file=sys.stderr)
    else:
        print(f"Using absolute cfg_path {cfg_path}", file=sys.stderr)
    config = ConfigParser()
    with cfg_path.open() as f:
        config.read_file(f)

    return config


def hosts_conf(cfg: CfgfileArgument) -> MemoryHostStore:
    """Read a hosts configuration file and return a MemoryHostStore

    Arguments:

    ``cfgfile``:
        The path to the config file, or a ConfigParser object.
        If a ConfigParser, it is used directly.
        If a relative path, it look relative to the progfigsite package root,
        then relative to the current working directory.

    An example hosts config file:

    .. code-block:: ini

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

    Hosts config files are designed to be composable with secrets config files for
    :meth:`progfiguration.sitehelpers.invconf.secrets_conf` --
    the two files can be combined into one and each function will read the appropriate section(s).
    """

    config = _parse_cfgfile_argument(cfg)

    hoststore = MemoryHostStore(
        groups={g: m.split() for g, m in config.items("groups")},
        node_function_map={n: f for n, f in config.items("node_function_map")},
        function_role_map={f: r.split() for f, r in config.items("function_role_map")},
    )

    return hoststore


def secrets_conf(cfg: CfgfileArgument) -> AgeSecretStore:
    """Read a secrets configuration file and return an AgeSecretStore

    Arguments:

    ``cfgfile``:
        The path to the config file, or a ConfigParser object.
        If a ConfigParser, it is used directly.
        If a relative path, it look relative to the progfigsite package root,
        then relative to the current working directory.

    An example secrets config file:

    .. code-block:: ini

        [secrets]
        # The controller has an age key which can be used to decrypt any secret.
        # When this file is not present, progfiguration will still work,
        # but activities that require the secret key will throw errors.
        controller_age_path = /path/to/controller.age

        # We must hard code the public key in this file as well,
        # so that it is available even when we aren't running on the controller.
        controller_age_pub = paste the public key here

        # The default/fallback location for the age key on each node.
        node_fallback_age_path = /etc/progfiguration/node.age

    Hosts config files are designed to be composable with secrets config files for
    :meth:`progfiguration.sitehelpers.invconf.hosts_conf` --
    the two files can be combined into one and each function will read the appropriate section(s).
    """

    config = _parse_cfgfile_argument(cfg)

    secretstore = AgeSecretStore(
        controller_age_pubkey=config.get("secrets", "controller_age_pub"),
        decryption_age_privkey_path_list=[
            config.get("secrets", "controller_age_path"),
            config.get("secrets", "node_fallback_age_path"),
        ],
    )

    return secretstore
