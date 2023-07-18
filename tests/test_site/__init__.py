"""Tests of inventory functionality using a test site."""

import pathlib
import sys
import unittest

from progfiguration import sitewrapper
from progfiguration.inventory import Inventory

from tests import PdbTestCase, pdbexc


class TestRun(PdbTestCase):
    @classmethod
    @pdbexc
    def setUpClass(cls):

        # Place the test progfigsite package on the path, and set it as the site package
        parent_path = pathlib.Path(__file__).parent
        nnss_path = pathlib.Path(parent_path, "nnss")
        sys.path.insert(0, str(nnss_path))
        sitewrapper.site_module_path = "nnss_progfigsite"

        cls.inventory = Inventory(sitewrapper.site.package_inventory_file, None)

        # if not cls.inventory.controller.age:
        #     raise Exception(
        #         "Controller age is not set - are you running this from the controller with a decrypted secrets volume?"
        #     )

    @pdbexc
    def test_inventory_all_roles(self):
        """Test that all roles can be instantiated

        Instantiation requires decrypting secrets (which requires the controller age),
        and properly dereferencing secrets and role results.
        """

        for nodename in self.inventory.nodes:
            for role in self.inventory.node_role_list(nodename):
                with self.subTest(msg=f"nodename={nodename}, role={role}"):
                    pass

    @pdbexc
    def test_list_nodes(self):
        """Find all nodes"""
        self.assertCountEqual(self.inventory.nodes, ["node1"])
        self.assertEqual(self.inventory.node("node1").node.address, "node1.example.mil")

    @pdbexc
    def test_list_groups(self):
        """Find all groups"""
        self.assertCountEqual(self.inventory.groups, ["universal", "group1"])

    @pdbexc
    def test_list_functions(self):
        """Find all functions"""
        self.assertCountEqual(self.inventory.functions, ["default", "func1"])

    @pdbexc
    def test_list_roles(self):
        """Find all roles"""
        self.assertCountEqual(self.inventory.roles, ["settz"])


if __name__ == "__main__":
    unittest.main()
