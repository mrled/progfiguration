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

        for nodename in self.nnss.progfigsite.inventory.nodes:
            for role in self.nnss.progfigsite.inventory.node_role_list(nodename, self.nnss.progfigsite.secretstore):
                with self.subTest(msg=f"nodename={nodename}, role={role}"):
                    pass

    @pdbexc
    def test_list_nodes(self):
        """Find all nodes"""
        self.assertCountEqual(self.nnss.progfigsite.inventory.nodes, ["node1"])
        self.assertEqual(self.nnss.progfigsite.inventory.node("node1").node.address, "node1.example.mil")

    @pdbexc
    def test_list_groups(self):
        """Find all groups"""
        self.assertCountEqual(self.nnss.progfigsite.inventory.groups, ["universal", "group1"])

    @pdbexc
    def test_list_functions(self):
        """Find all functions"""
        self.assertCountEqual(self.nnss.progfigsite.inventory.functions, ["default", "func1"])

    @pdbexc
    def test_list_roles(self):
        """Find all roles"""
        self.assertCountEqual(self.nnss.progfigsite.inventory.roles, ["settz"])

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
        test_password = self.nnss.progfigsite.secretstore.get_secret("special", "controller", "test_password")
        decrypted_test_pass = test_password.decrypt()
        self.assertEqual(decrypted_test_pass, "p@ssw0rd")


if __name__ == "__main__":
    unittest.main()
