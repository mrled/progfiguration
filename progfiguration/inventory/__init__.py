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
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Literal, Protocol, runtime_checkable

from progfiguration import logger, sitewrapper
from progfiguration.inventory.roles import ProgfigurationRole, collect_role_arguments
from progfiguration.localhost import LocalhostLinux


class Inventory:
    """An site's inventory"""

    def __init__(
        self,
        invfile: Traversable | Path | configparser.ConfigParser,
    ):
        """Initializer parameters:

        * `invfile`: A path to an inventory configuration file.
          Alternatively, a `configparser.ConfigParser` object from a valid configuration file.
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
        You can then call `.apply()` or `.calculations()` on the role.

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


@runtime_checkable
class Secret(Protocol):
    """An abstract class for secrets"""

    _cache: Any
    """An optional cache for the decrypted secret value.

    Used by the default implementation of the `value` property.
    """

    secret: str
    """The encrypted secret value."""

    def __init__(self):
        self._cache = None

    @property
    def value(self) -> str:
        """Return the secret value.

        This default implementation caches the result in the ``_cache`` attribute.
        """
        if self._cache is None:
            self._cache = self.decrypt()
        return self._cache

    def decrypt(self) -> str:
        """Decrypt the secret."""
        raise NotImplementedError("decrypt not implemented")


@runtime_checkable
class SecretStore(Protocol):
    """A protocol for secret storage and encryption.

    Implementations are encouraged to cache results.

    Secrets are stored in three different collections.
    "node" and "group" collections then use the node/group name.
    The only name used in the "special" collection is "controller",
    for secrets that only the controller should be able to decrypt.
    """

    def list_secrets(self, collection: Literal["node", "group", "special"], name: str) -> List[str]:
        """List secrets."""
        raise NotImplementedError("list_secrets not implemented")

    def get_secret(self, collection: Literal["node", "group", "special"], name: str, secret_name: str) -> Secret:
        """Retrieve a secret from the secret store.

        This operation returns an opaque Secret type.
        The secret does not have to be decrypted yet,
        but can be, depending on the Secret implementation.
        """
        raise NotImplementedError("get_secret not implemented")

    def set_secret(
        self,
        inventory: Inventory,
        name: str,
        value: str,
        nodes: List[str],
        groups: List[str],
        controller_key: bool,
        store: bool = False,
    ) -> str:
        """Set a secret in the secret store.

        This operation encrypts the secret and stores it in the secret store.

        If ``store`` is True, persist the encrypted value to secret storage.
        Implementations must make sure that the controller will be able to decrypt.
        If ``store`` is False, the secret is just being displayed to the user or something.

        Return the encrypted value.
        (If we don't return the encrypted value, it makes no sense to have a store parameter.)
        """
        raise NotImplementedError("set_secret not implemented")


def get_inherited_secret(store: SecretStore, inventory: Inventory, node: str, secret_name: str) -> Secret:
    """Get a secret for a node, inheriting from groups if necessary."""
    secret = store.get_secret("node", node, secret_name)
    if secret is None:
        # "universal" will be the first group; we want to check it last.
        # Reminder that all other group order is not guaranteed.
        for group in reversed(inventory.node_groups[node]):
            secret = store.get_secret("group", group, secret_name)
            if secret is not None:
                break
    return secret
