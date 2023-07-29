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

import configparser
from importlib.abc import Traversable
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Union

from progfiguration import logger, sitewrapper
from progfiguration.age import AgeKey, AgeSecret, encrypt
from progfiguration.inventory.roles import ProgfigurationRole, collect_role_arguments
from progfiguration.localhost import LocalhostLinux
from progfiguration.progfigtypes import AnyPathOrStr


class Inventory:
    """An site's inventory"""

    def __init__(
        self,
        invfile: Traversable | Path | configparser.ConfigParser,
        progfigsite_package_path: str,
        age_privkey: Optional[str] = None,
        current_node: Optional[str] = None,
    ):
        """Initializer parameters:

        * `invfile`: A path to an inventory configuration file.
          Alternatively, a `configparser.ConfigParser` object from a valid configuration file.
        * `progfigsite_package_path`: The path to the progfigsite package.
          This is a Python package path to the progfigsite package.
        * `age_privkey`: Use this path to an age private key.
          If not passed, try to find the appropriate node/controller age key.
        * `current_node`: The name of the current node, if applicable.
          If `age_privkey` is not passed, this is used to find the appropriate node age key.
        """

        if isinstance(invfile, configparser.ConfigParser):
            self._config = invfile
        else:
            self._config = configparser.ConfigParser()
            with invfile.open() as f:
                self._config.read_file(f)

        self.localhost = LocalhostLinux()
        """A localhost object

        TODO: probably should not use this
        """

        self.node_function = {}
        """A dict where keys are node names and values are function names"""
        for node, func in self._config.items("node_function_map"):
            self.node_function[node] = func

        self.function_roles = {}
        """ a dict where keys are function names and value are lists of role names"""
        for func, roles in self._config.items("function_role_map"):
            self.function_roles[func] = roles.split()

        self.group_members = {"universal": [n for n in self.node_function.keys()]}
        """a dict where keys are group names and values are lists of node names"""
        # (Prepend the universal group to the list of groups)
        for group, members in self._config.items("groups"):
            self.group_members[group] = members.split()

        self._node_groups: Dict[str, List[str]] = {}
        self._function_nodes: Dict[str, List[str]] = {}

        self._node_modules: Dict[str, ModuleType] = {}
        self._group_modules: Dict[str, ModuleType] = {}
        self._role_modules: Dict[str, ModuleType] = {}
        self._node_roles: Dict[str, Dict[str, ProgfigurationRole]] = {}

        self._node_secrets: Dict[str, Dict[str, AgeSecret]] = {}
        self._group_secrets: Dict[str, Dict[str, AgeSecret]] = {}
        self._controller_secrets: Dict[str, AgeSecret] = {}

        self.controller = Controller(
            self._config.get("general", "controller_age_pub"), self._config.get("general", "controller_age_path")
        )
        """A `Controller`, for keeping track of the age key

        TODO: weird API, maybe get rid of the .controller property
        """

        # Get the age key path for this node, if the node is specified and has a key defined
        current_node_age_key_path = None
        if current_node is not None:
            try:
                current_node_age_key_path = self.node(current_node).node.age_key_path
            except (KeyError, ModuleNotFoundError):
                pass

        def maybe_get_age_path() -> Optional[str]:
            """Find the age path to a private key if possible

            Lookup order, highest priority first:
            * A key passed to the class initializer directly, if present
            * The controller key, if available
            * The key for the current node, if running from a node with an available key
            * None
            """
            for possible_key in [
                age_privkey,
                self.controller.agepath,
                current_node_age_key_path,
                self._config.get("general", "node_fallback_age_path"),
            ]:
                if possible_key and os.path.exists(possible_key):
                    logger.debug(f"Found age key {possible_key}")
                    return possible_key
                else:
                    logger.debug(f"No age key found at {possible_key}, continuing...")
            else:
                logger.debug("No age key found")
                return None

        self.age_path: Union[str, None] = maybe_get_age_path()
        """The path to the age private key currently in scope

        If one cannot be found, this will be None.

        Depending on context, this might be the controller key, an individual node's key,
        or one passed in from the  command line.
        """

    @property
    def groups(self) -> List[str]:
        """All groups, in undetermined order"""
        return list(self.group_members.keys())

    @property
    def nodes(self) -> List[str]:
        """All nodes, in undetermined order"""
        return list(self.node_function.keys())

    @property
    def functions(self) -> List[str]:
        """All functions, in undetermined order"""
        return list(self.function_roles.keys())

    @property
    def roles(self) -> List[str]:
        """All roles, in undetermined order"""
        result = set()
        for func_role_list in self.function_roles.values():
            result.update(func_role_list)
        return list(result)

    @property
    def node_groups(self) -> Dict[str, List[str]]:
        """A dict, containing node:grouplist mappings"""
        if not self._node_groups:
            self._node_groups = {}

            # All nodes should be listed in the nodeFunctionMap, so we first give them all an empty group list.
            # This gets us all nodes, even if they are not members of any explicit group.
            for node in self.node_function.keys():
                self._node_groups[node] = []

            # Now we traverse the groupNodeMap and fill in the group list
            for group, members in self.group_members.items():
                for member in members:
                    self._node_groups[member].append(group)

        return self._node_groups

    @property
    def function_nodes(self) -> Dict[str, List[str]]:
        """A dict, containing function:nodelist mappings"""
        if not self._function_nodes:
            self._function_nodes = {}
            for node, function in self.node_function.items():
                if function not in self._function_nodes:
                    self._function_nodes[function] = []
                self._function_nodes[function].append(node)
        return self._function_nodes

    def node_rolename_list(self, nodename: str) -> List[str]:
        """A list of all rolenames for a given node"""
        return self.function_roles[self.node_function[nodename]]

    def node(self, name: str) -> ModuleType:
        """The Python module for a given node"""
        if name not in self._node_modules:
            module = sitewrapper.site_submodule(f"nodes.{name}")
            self._node_modules[name] = module
        return self._node_modules[name]

    def group(self, name: str) -> ModuleType:
        """The Python module for a given group"""
        if name not in self._group_modules:
            module = sitewrapper.site_submodule(f"groups.{name}")
            self._group_modules[name] = module
        return self._group_modules[name]

    def role_module(self, name: str) -> ModuleType:
        """The Python module for a given role"""
        if name not in self._role_modules:
            module = sitewrapper.site_submodule(f"roles.{name}")
            self._role_modules[name] = module
        return self._role_modules[name]

    def node_role(self, nodename: str, rolename: str) -> ProgfigurationRole:
        """A dict of `{nodename: {rolename: ProgfigurationRole}}`

        Get an instantiated `progfiguration.inventory.roles.ProgfigurationRole` object for a given node and role.

        We collect all arguments required to instantiate the role,
        including the superclass arguments like rolepkg and localhost,
        as well as role-specific arguments accepted by the given `ProgfigurationRole` subclass
        and defined as a default argument or in the group or node argument dicts.
        You can then call `.apply()` or `.results()` on the role.

        Results are cached for subsequent calls.
        """
        if nodename not in self._node_roles:
            self._node_roles[nodename] = {}
        if rolename not in self._node_roles[nodename]:

            # rolepkg is a string containing the package name of the role, like 'progfigsite.roles.role_name'
            rolepkg = self.role_module(rolename).__package__

            # The class it the subclass of ProgfigurationRole that implements the role
            role_cls = self.role_module(rolename).Role

            # Get a list of all the groups this node is a member of so that we can get any role arg definitions they may have
            groupmods = {}
            for groupname in self.node_groups[nodename]:
                groupmods[groupname] = self.group(groupname)

            # Get the node module so we can get any role arg definitions it may have
            node = self.node(nodename).node

            # Collect all the arguments we need to instantiate the role class
            # This function finds the most specific definition of each argument
            roleargs = collect_role_arguments(self, nodename, node, groupmods, rolename)

            # Instantiate the role class, now that we have all the arguments we need
            try:
                role = role_cls(name=rolename, localhost=self.localhost, inventory=self, rolepkg=rolepkg, **roleargs)
            except Exception as exc:
                msg = f"Error instantiating role {rolename} for node {nodename}: {exc}"
                if isinstance(exc, AttributeError) and exc.args[0].startswith("can't set attribute"):
                    msg += " This might happen if you have two properties with the same name (perhaps one as a function with a @property decorator)."
                raise Exception(msg) from exc

            # And set the role in the cache
            self._node_roles[nodename][rolename] = role

        return self._node_roles[nodename][rolename]

    def node_role_list(self, nodename: str) -> list[ProgfigurationRole]:
        """A list of all instantiated roles for a given node"""
        return [self.node_role(nodename, rolename) for rolename in self.node_rolename_list(nodename)]

    def get_secrets(self, filename: AnyPathOrStr) -> Dict[str, AgeSecret]:
        """Retrieve secrets from a file.

        If the file is not found, just return an empty dict.
        """
        if isinstance(filename, str):
            filename = Path(filename)
        try:
            with filename.open() as fp:
                contents = json.load(fp)
                encrypted_secrets = {k: AgeSecret(v) for k, v in contents.items()}
                return encrypted_secrets
        except FileNotFoundError:
            return {}

    def get_node_secrets(self, nodename: str) -> Dict[str, AgeSecret]:
        """A Dict of secrets for a given node"""
        if nodename not in self._node_secrets:
            self._node_secrets[nodename] = self.get_secrets(self.node_secrets_file(nodename))
        return self._node_secrets[nodename]

    def get_group_secrets(self, groupname: str) -> Dict[str, Any]:
        """A Dict of secrets for a given group"""
        if groupname not in self._group_secrets:
            self._group_secrets[groupname] = self.get_secrets(self.group_secrets_file(groupname))
        return self._group_secrets[groupname]

    def get_controller_secrets(self) -> Dict[str, Any]:
        """A Dict of secrets for the controller"""
        if not self._controller_secrets:
            sfile = sitewrapper.site_submodule_resource("", "controller.secrets.json")
            self._controller_secrets = self.get_secrets(sfile)
        return self._controller_secrets

    def _set_secrets(self, filepath: Path, secrets: Dict[str, AgeSecret]):
        """Set the contents of a secrets file"""
        file_contents = {k: v.secret for k, v in secrets.items()}
        with filepath.open("w") as fp:
            json.dump(file_contents, fp)

    def group_secrets_file(self, group: str) -> Path:
        """The path to the secrets file for a given group"""
        sfile = sitewrapper.site_submodule_resource("groups", f"{group}.secrets.json")
        return sfile

    def node_secrets_file(self, node: str) -> Path:
        """The path to the secrets file for a given node"""
        sfile = sitewrapper.site_submodule_resource("nodes", f"{node}.secrets.json")
        return sfile

    def controller_secrets_file(self) -> Path:
        """The path to the secrets file for the controller"""
        sfile = sitewrapper.site_submodule_resource("", "controller.secrets.json")
        return sfile

    def set_node_secret(self, nodename: str, secretname: str, encrypted_value: str):
        """Set a secret for a node"""
        self.get_node_secrets(nodename)  # Ensure it's cached
        self._node_secrets[nodename][secretname] = AgeSecret(encrypted_value)
        self._set_secrets(self.node_secrets_file(nodename), self._node_secrets[nodename])

    def set_group_secret(self, groupname: str, secretname: str, encrypted_value: str):
        """Set a secret for a group"""
        self.get_group_secrets(groupname)  # Ensure it's cached
        self._group_secrets[groupname][secretname] = AgeSecret(encrypted_value)
        self._set_secrets(self.group_secrets_file(groupname), self._group_secrets[groupname])

    def set_controller_secret(self, secretname: str, encrypted_value: str):
        """Set a secret for the controller"""
        self.get_controller_secrets()  # Ensure it's cached
        self._controller_secrets[secretname] = AgeSecret(encrypted_value)
        self._set_secrets(self.controller_secrets_file(), self._controller_secrets)

    def encrypt_secret(
        self, name: str, value: str, nodes: List[str], groups: List[str], controller_key: bool, store: bool = False
    ):
        """Encrypt a secret for some list of nodes and groups.

        Always encrypt for the controller so that it can decrypt too.
        """

        recipients = nodes.copy()

        for group in groups:
            recipients += self.group_members[group]
        recipients = list(set(recipients))

        nmods = [self.node(n) for n in recipients]
        pubkeys = [nm.node.age_pubkey for nm in nmods]

        # We always encrypt for the controller when storing, so that the controller can decrypt too
        if controller_key or store:
            pubkeys += [self.controller.agepub]

        encrypted_value = encrypt(value, pubkeys)

        if store:
            for node in nodes:
                self.set_node_secret(node, name, encrypted_value)
            for group in groups:
                self.set_group_secret(group, name, encrypted_value)
            if controller_key:
                self.set_controller_secret(name, encrypted_value)

        return (encrypted_value, pubkeys)


class Controller:
    """A Controller object

    If this program is running on the controller, it includes the private key;
    otherwise, it just includes the public key.
    """

    age: Optional[AgeKey]
    """An age key object, if the private key is available"""

    agepub: str
    """A string containing the age public key"""

    agepath: Optional[str]
    """The path to the controller age private key, if available"""

    def __init__(self, agepub: str, privkeypath: str):
        """Initializer params:

        * `agepub`:         The path to the controller age public key
        * `privkeypath`:    The path to the controller age private key
        """
        if privkeypath and os.path.exists(privkeypath):
            self.age = AgeKey.from_file(privkeypath)
        else:
            self.age = None
        self.agepub = agepub
        self.agepath = privkeypath

    def __str__(self):
        return f"Controller(agepub={self.agepub}, agepath={self.agepath}, age={self.age})"
