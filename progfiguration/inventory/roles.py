"""Applying and working with roles

Note that we have to ignore type checking on string references to Inventory here.
The inventory module imports this module,
so we cannot import it,
or we will get a circular import.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib.abc import Traversable
from importlib.resources import files as importlib_resources_files
from types import ModuleType
from typing import Any, Optional

from progfiguration.inventory.nodes import InventoryNode
from progfiguration.localhost import LocalhostLinux


class RoleArgumentReference(ABC):
    """A special kind of role argument that is dereferenced at runtime.

    This is used to allow roles to reference arguments from other roles

    Role arguments are often used as-is, but some kinds of arguments are references.
    A reference is any object that has a dereference() method.
    Some examples from progfiguration core:

    * age.AgeSecretReference: Decrypt the secret using the age key
    * RoleCalculationReference: Get the calculation from the referenced role

    Sites can define their own argument references.

    Custom argument references to not need to inherit from this class,
    but they must have a dereference() method with the same signature.
    """

    @abstractmethod
    def dereference(
        self,
        nodename: str,
        inventory: "Inventory",  # type: ignore
    ) -> Any:
        """Get the final value of a role argument for a node.

        Arguments to this method:

        * nodename:     The name of the node that the argument is being applied to
        * inventory:    The inventory object

        This function must retrieve or calculate the final value
        from its internal data and these arguments.
        """
        pass


@dataclass
class RoleCalculationReference(RoleArgumentReference):
    """A reference to a calculation from a role

    This is used to allow roles to reference calculations from other roles
    """

    role: str
    calcname: str

    def dereference(
        self,
        nodename: str,
        inventory: "Inventory",  # type: ignore
    ) -> Any:
        return inventory.node_role(nodename, self.role).calculations()[self.calcname]


@dataclass(kw_only=True)
class ProgfigurationRole(ABC):
    """A role that can be applied to a node

    Required attributes:

    * name: The name of the role
    * localhost: A localhost object
    * inventory: An inventory object
    * rolepkg: The package that the role is defined in,
        used to determine the path to the role's templates.

    Required methods:

    * apply(): Apply the role to the node

    Optional methods:

    * calculations(): Return a dict of data the role can calculate
      from its arguments and internal state before it is applied.
      This data can be referenced by other roles.
      For instance, a role that creates a user
      might calculate the user's homedir path like '/home/username',
      and return a calculation like {'homedir': '/home/username'}.
      The user may or may not have been created when it returns this data,
      and the path may or may not exist until the role actually runs.
    """

    # Note that you cannot override properties in a subclass of a dataclass.
    # Take care when adding new attributes here.
    name: str
    localhost: LocalhostLinux
    inventory: "Inventory"  # type: ignore
    rolepkg: str

    # This is just a cache
    _rolefiles: Optional[Any] = None

    @abstractmethod
    def apply(self, **kwargs):
        pass

    def calculations(self):
        return {}

    def role_file(self, filename: str) -> Traversable:
        """Get the path to a file in the role's package

        This works whether we're installed from pip, checked out from git, or running from a pyz file.
        """
        if not self._rolefiles:
            self._rolefiles = importlib_resources_files(self.rolepkg)
        return self._rolefiles.joinpath(filename)


def collect_role_arguments(
    inventory: "Inventory",  # type: ignore
    nodename: str,
    node: InventoryNode,
    nodegroups: dict[str, ModuleType],
    rolename: str,
):
    """Collect all the arguments for a role

    Find the arguments in the following order:

    * Default role arguments from the ProgfigurationRole subclass
    * Arguments from the universal group
    * Arguments from other groups (in an undefined order)
    * Arguments from the node itself

    Dereference any arg refs.
    """
    groupmods = {}
    for groupname in inventory.node_groups[nodename]:
        groupmods[groupname] = inventory.group(groupname)

    roleargs = {}

    for groupname, gmod in nodegroups.items():
        group_rolevars = gmod.group["roles"].get(rolename, {})
        for key, value in group_rolevars.items():
            roleargs[key] = value

    # Apply any role arguments from the node itself
    node_rolevars = node.roles.get(rolename, {})
    for key, value in node_rolevars.items():
        roleargs[key] = value

    for key, value in roleargs.items():
        if hasattr(value, "dereference"):
            roleargs[key] = value.dereference(nodename, inventory)

    return roleargs
