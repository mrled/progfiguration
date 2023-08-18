"""A memory-based inventory store

The store is designed to be persisted to disk,
perhaps with a configuration file or by defining the nodes/groups/etc in the site's root module.
"""


from types import ModuleType
from typing import Dict, List
from progfiguration import sitewrapper
from progfiguration.inventory.invstores import SecretStore
from progfiguration.inventory.roles import ProgfigurationRole, collect_role_arguments

from progfiguration.localhost import LocalhostLinux


class MemoryHostStore:
    """An site's inventory"""

    def __init__(
        self,
        groups: Dict[str, List[str]],
        node_function_map: Dict[str, str],
        function_role_map: Dict[str, List[str]],
    ):

        self.localhost = LocalhostLinux()
        """A localhost object

        TODO: probably should not use this
        """

        self.node_function = node_function_map
        """A dict where keys are node names and values are function names"""

        self.function_roles = function_role_map
        """ a dict where keys are function names and value are lists of role names"""

        # (Prepend the universal group to the list of groups)
        self.group_members = {"universal": [n for n in self.node_function.keys()], **groups}
        """a dict where keys are group names and values are lists of node names"""

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
            roleargs = collect_role_arguments(self, secretstore, nodename, node, groupmods, rolename)

            # Instantiate the role class, now that we have all the arguments we need
            try:
                role = role_cls(name=rolename, localhost=self.localhost, hoststore=self, rolepkg=rolepkg, **roleargs)
            except Exception as exc:
                msg = f"Error instantiating role {rolename} for node {nodename}: {exc}"
                if isinstance(exc, AttributeError) and exc.args[0].startswith("can't set attribute"):
                    msg += " This might happen if you have two properties with the same name (perhaps one as a function with a @property decorator)."
                raise Exception(msg) from exc

            # And set the role in the cache
            self._node_roles[nodename][rolename] = role

        return self._node_roles[nodename][rolename]

    def node_role_list(self, nodename: str, secretstore: SecretStore) -> list[ProgfigurationRole]:
        """A list of all instantiated roles for a given node"""
        return [self.node_role(secretstore, nodename, rolename) for rolename in self.node_rolename_list(nodename)]
