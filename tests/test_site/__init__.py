"""Tests of inventory functionality using a test site."""

import configparser
import os
import pathlib
import subprocess
from typing import List
import tempfile
import unittest

from progfiguration import example_site, progfigbuild, sitewrapper
from progfiguration.inventory import Inventory

from tests import PdbTestCase, pdbexc, skipUnlessAnyEnv


class TestRun(PdbTestCase):
    @classmethod
    @pdbexc
    def setUpClass(cls):

        # Find nnss progfigsite paths
        parent_path = pathlib.Path(__file__).parent
        nnss_path = pathlib.Path(parent_path / "nnss")
        cls.nnss_progfigsite_path = pathlib.Path(nnss_path / "nnss_progfigsite")
        nnss_controller_age = pathlib.Path(nnss_path / "controller.age")

        # Place the test progfigsite package on the path, and set it as the site package
        sitewrapper.set_site_module_filepath(str(cls.nnss_progfigsite_path))

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

    # TODO: move these tests to another test file
    # TODO: move NNSS to some shared location so that we can use it in other test files
    @pdbexc
    @skipUnlessAnyEnv("PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_PACKAGING")
    def test_package_example_site(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pyzfile = pathlib.Path(tmpdir) / "test.pyz"
            progfigbuild.build_progfigsite_zipapp(pyzfile, pathlib.Path(example_site.__file__).parent)
            self.assertTrue(pyzfile.exists())
            result = subprocess.run([str(pyzfile), "version"], check=True, capture_output=True)
            stdout = result.stdout.decode("utf-8").strip()
            self.assertTrue("progfiguration core" in stdout)
            self.assertTrue(example_site.site_name in stdout)
            self.assertTrue(example_site.site_description in stdout)

    @pdbexc
    @skipUnlessAnyEnv("PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_PACKAGING")
    def test_package_nnss(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pyzfile = pathlib.Path(tmpdir) / "test.pyz"
            progfigbuild.build_progfigsite_zipapp(pyzfile, self.nnss_progfigsite_path)
            self.assertTrue(pyzfile.exists())
            result = subprocess.run([str(pyzfile), "version"], check=True, capture_output=True)
            stdout = result.stdout.decode("utf-8").strip()
            self.assertTrue("progfiguration core" in stdout)
            self.assertTrue(sitewrapper.progfigsite.site_name in stdout)
            self.assertTrue(sitewrapper.progfigsite.site_description in stdout)


if __name__ == "__main__":
    unittest.main()
