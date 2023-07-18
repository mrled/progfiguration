"""Tests of inventory functionality using a test site."""

import configparser
import pathlib
import unittest

from progfiguration import sitewrapper
from progfiguration.inventory import Inventory

from tests import PdbTestCase, pdbexc


class TestRun(PdbTestCase):
    @classmethod
    @pdbexc
    def setUpClass(cls):

        # Find nnss progfigsite paths
        parent_path = pathlib.Path(__file__).parent
        nnss_path = pathlib.Path(parent_path / "nnss")
        nnss_progfigsite_path = pathlib.Path(nnss_path / "nnss_progfigsite")
        nnss_controller_age = pathlib.Path(nnss_path / "controller.age")

        # Place the test progfigsite package on the path, and set it as the site package
        sitewrapper.set_site_module_filepath(str(nnss_progfigsite_path))

        cls.invfilecfg = configparser.ConfigParser()
        cls.invfilecfg.read(sitewrapper.site_submodule_resource("", "inventory.conf"))

        # Override the controller age path to point to the test controller age,
        # no matter where it is on the filesystem.
        cls.invfilecfg.set("general", "controller_age_path", str(nnss_controller_age))

        cls.inventory = Inventory(cls.invfilecfg, str(nnss_controller_age))

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

    # @pdbexc
    # def test_controller_encrypt(self):
    #     """Test encrypting a secret

    #     This actually creates an encrypted value on disk.
    #     However, age changes the salt every time something is encrypted,
    #     so we can't test the result for a specific known value,
    #     and it will change the secret file on every run,
    #     which is annoying for version control.
    #     """
    #     encrypted_value, pubkeys = self.inventory.encrypt_secret("test_password", "p@ssw0rd", [], [], True, store=True)

    @pdbexc
    def test_controller_decrypt(self):
        csecrets = self.inventory.get_controller_secrets()
        decrypted_test_pass = csecrets["test_password"].decrypt(self.inventory.controller.agepath)
        self.assertEqual(decrypted_test_pass, "p@ssw0rd")


if __name__ == "__main__":
    unittest.main()
