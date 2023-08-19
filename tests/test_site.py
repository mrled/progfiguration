"""Tests of inventory functionality using a test site."""

import unittest
from progfiguration.util import import_module_from_filepath

from tests import PdbTestCase, pdbexc
from tests.data import NnssTestData, SimpleExampleTestData

from progfiguration.progfigsite_validator import validate


class TestRun(PdbTestCase):
    @classmethod
    @pdbexc
    def setUpClass(cls):
        cls.nnss = NnssTestData()
        cls.examplesite = SimpleExampleTestData()

    @pdbexc
    def test_example_sites_validate(self):
        """Test that the test site validates"""

        example_site_module, example_site_modpath = import_module_from_filepath(
            self.examplesite.progfigsite_path.as_posix()
        )
        example_site_validation = validate(example_site_modpath)
        self.assertTrue(example_site_validation.is_valid)

        nnss_module, nnss_modpath = import_module_from_filepath(self.examplesite.progfigsite_path.as_posix())
        nnss_validation = validate(nnss_modpath)
        self.assertTrue(nnss_validation.is_valid)

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
