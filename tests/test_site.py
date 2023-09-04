"""Tests of inventory functionality using a test site."""

import unittest

from tests import PdbTestCase, pdbexc
from tests.data import nnss_test_data, simple_example_test_data

from progfiguration import sitewrapper
from progfiguration.progfigsite_validator import validate


class TestRun(PdbTestCase):
    @pdbexc
    def test_example_sites_validate(self):
        """Test that the test site validates"""
        with simple_example_test_data as exsite:
            exsite_validation = validate(exsite.progfigsite_name)
            self.assertTrue(exsite_validation.is_valid)

    @pdbexc
    def test_nnss_validate(self):
        """Test that the NNSS validates"""
        with nnss_test_data as nnss:
            nnss_validation = validate(nnss.progfigsite_name)
            self.assertTrue(nnss_validation.is_valid)

    @pdbexc
    def test_inventory_all_roles(self):
        """Test that all roles can be instantiated

        Instantiation requires decrypting secrets (which requires the controller age),
        and properly dereferencing secrets and role calculations.
        """
        with nnss_test_data as nnss:
            for nodename in nnss.inventory.hoststore.nodes:
                for role in nnss.inventory.hoststore.node_role_list(nodename, nnss.inventory.secretstore):
                    with self.subTest(msg=f"nodename={nodename}, role={role}"):
                        pass

    @pdbexc
    def test_list_nodes(self):
        """Find all nodes"""
        with nnss_test_data as nnss:
            self.assertCountEqual(nnss.inventory.hoststore.nodes, ["node1"])
            self.assertEqual(nnss.inventory.hoststore.node("node1").node.address, "node1.example.mil")

    @pdbexc
    def test_list_groups(self):
        """Find all groups"""
        with nnss_test_data as nnss:
            self.assertCountEqual(nnss.inventory.hoststore.groups, ["universal", "group1"])

    @pdbexc
    def test_list_functions(self):
        """Find all functions"""
        with nnss_test_data as nnss:
            self.assertCountEqual(nnss.inventory.hoststore.functions, ["default", "func1"])

    @pdbexc
    def test_list_roles(self):
        """Find all roles"""
        with nnss_test_data as nnss:
            self.assertCountEqual(nnss.inventory.hoststore.roles, ["settz"])


if __name__ == "__main__":
    unittest.main()
