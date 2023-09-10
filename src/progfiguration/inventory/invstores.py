"""Inventory store

Protocols for inventory stores (host stores and secret stores).
"""

from __future__ import annotations

from types import ModuleType
from typing import Any, Dict, List, Literal, Protocol, runtime_checkable
from progfiguration.inventory.nodes import InventoryNode

from progfiguration.inventory.roles import ProgfigurationRole, RoleArgumentReference
from progfiguration.localhost import LocalhostLinux


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
class HostStore(Protocol):
    """Hosts, groups, functions, and roles for a site"""

    localhost: LocalhostLinux
    """A localhost object

    TODO: can we get rid of this?
    """

    node_function: Dict[str, str]
    """A dict where keys are node names and values are function names"""

    function_roles: Dict[str, List[str]]
    """A dict where keys are function names and value are lists of role names"""

    group_members: Dict[str, List[str]]
    """A dict where keys are group names and values are lists of node names"""

    @property
    def groups(self) -> List[str]:
        """All groups, in undetermined order"""
        raise NotImplementedError("groups not implemented")

    @property
    def nodes(self) -> List[str]:
        """All nodes, in undetermined order"""
        raise NotImplementedError("nodes not implemented")

    @property
    def functions(self) -> List[str]:
        """All functions, in undetermined order"""
        raise NotImplementedError("functions not implemented")

    @property
    def roles(self) -> List[str]:
        """All roles, in undetermined order"""
        raise NotImplementedError("roles not implemented")

    @property
    def node_groups(self) -> Dict[str, List[str]]:
        """A dict, containing node:grouplist mappings"""
        raise NotImplementedError("node_groups not implemented")

    @property
    def function_nodes(self) -> Dict[str, List[str]]:
        """A dict, containing function:nodelist mappings"""
        raise NotImplementedError("function_nodes not implemented")

    def node_rolename_list(self, nodename: str) -> List[str]:
        """A list of all rolenames for a given node"""
        raise NotImplementedError("node_rolename_list not implemented")

    def node(self, name: str) -> ModuleType:
        """The Python module for a given node

        TODO: should return an InventoryNode instead of a ModuleType.
        """
        raise NotImplementedError("node not implemented")

    def group(self, name: str) -> ModuleType:
        """The Python module for a given group

        TODO: should return a dict instead of a ModuleType.
        """
        raise NotImplementedError("group not implemented")

    def role_module(self, name: str) -> ModuleType:
        """The Python module for a given role

        TODO: should return a ProgfigurationRole subclass instead of a ModuleType.
        """
        raise NotImplementedError("role_module not implemented")

    def node_role(self, secretstore: SecretStore, nodename: str, rolename: str) -> ProgfigurationRole:
        """A dict of `{nodename: {rolename: ProgfigurationRole}}`

        Get an instantiated `progfiguration.inventory.roles.ProgfigurationRole` object for a given node and role.

        We collect all arguments required to instantiate the role,
        including the superclass arguments like rolepkg and localhost,
        as well as role-specific arguments accepted by the given `ProgfigurationRole` subclass
        and defined as a default argument or in the group or node argument dicts.
        You can then call `.apply()` or `.calculations()` on the role.

        Results are cached for subsequent calls.
        """
        raise NotImplementedError("node_role not implemented")

    def node_role_list(self, nodename: str, secretstore: SecretStore) -> list[ProgfigurationRole]:
        """A list of all instantiated roles for a given node

        TODO: Deprecate this, it's just a wrapper around node_role anyway.
        """
        raise NotImplementedError("node_role_list not implemented")


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

        If the secret does not exist, raise a KeyError.
        """
        raise NotImplementedError("get_secret not implemented")

    def encrypt_secret(
        self,
        hoststore: HostStore,
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
        raise NotImplementedError("encrypt_secret not implemented")

    def apply_cli_arguments(self, args: Dict[str, str]) -> None:
        """Apply arguments from the command line

        Arguments are passed as comma-separated key/value pairs,
        like ``--secret-store-arguments key1=value1,key2=value2``
        and then parsed into a dict.
        """
        raise NotImplementedError("apply_cli_arguments not implemented")

    def find_node_key(self, node: InventoryNode):
        """If called, this function should find the decryption key for a node.

        It may be called by the progfigsite command-line program if the user specifies a node.
        The implementation may look up the key in the node's sitedata.
        """
        raise NotImplementedError("find_node_key not implemented")


def get_inherited_secret(hoststore: HostStore, secretstore: SecretStore, node: str, secret_name: str) -> Secret:
    """Get a secret for a node, inheriting from groups if necessary."""
    secret = None
    # "universal" will be the first group; we want to check it last.
    # Reminder that all other group order is not guaranteed.
    nodegroups = list(reversed(hoststore.node_groups[node]))
    try:
        return secretstore.get_secret("node", node, secret_name)
    except KeyError:
        for group in nodegroups:
            try:
                return secretstore.get_secret("group", group, secret_name)
            except KeyError:
                pass
    raise KeyError(f"Secret {secret_name} not found for node {node}, including searching groups {nodegroups}")


class SecretReference(RoleArgumentReference):
    """A reference to a secret by name

    This is a wrapper type that allows us to pass around a reference to a secret
    without having to know the secret's value.
    """

    name: str
    """The name of the secret"""

    def dereference(
        self,
        nodename: str,
        hoststore: "HostStore",  # type: ignore
        secretstore: "SecretStore",  # type: ignore
    ) -> Any:
        secret = get_inherited_secret(hoststore, secretstore, nodename, self.name)
        value = secret.decrypt()
        return value
