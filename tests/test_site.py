"""Tests of inventory functionality using a test site."""

import unittest

from tests import PdbTestCase, pdbexc
from tests.data import NnssTestData


class TestRun(PdbTestCase):
    @classmethod
    @pdbexc
    def setUpClass(cls):
        cls.nnss = NnssTestData()

    @pdbexc
    def test_inventory_all_roles(self):
        """Test that all roles can be instantiated

        Instantiation requires decrypting secrets (which requires the controller age),
        and properly dereferencing secrets and role calculations.
        """

        for nodename in self.nnss.progfigsite.hoststore.nodes:
            for role in self.nnss.progfigsite.hoststore.node_role_list(nodename, self.nnss.progfigsite.secretstore):
                with self.subTest(msg=f"nodename={nodename}, role={role}"):
                    pass

    @pdbexc
    def test_list_nodes(self):
        """Find all nodes"""
        self.assertCountEqual(self.nnss.progfigsite.hoststore.nodes, ["node1"])
        self.assertEqual(self.nnss.progfigsite.hoststore.node("node1").node.address, "node1.example.mil")

    @pdbexc
    def test_list_groups(self):
        """Find all groups"""
        self.assertCountEqual(self.nnss.progfigsite.hoststore.groups, ["universal", "group1"])

    @pdbexc
    def test_list_functions(self):
        """Find all functions"""
        self.assertCountEqual(self.nnss.progfigsite.hoststore.functions, ["default", "func1"])

    @pdbexc
    def test_list_roles(self):
        """Find all roles"""
        self.assertCountEqual(self.nnss.progfigsite.hoststore.roles, ["settz"])


if __name__ == "__main__":
    unittest.main()
