"""Tests of inventory functionality using a test site."""

import unittest
from progfiguration.sitehelpers.agesecrets import AgeSecret

from tests import PdbTestCase, pdbexc
from tests.data import nnss_test_data


class TestRun(PdbTestCase):

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
        with nnss_test_data as nnss:
            test_password = nnss.inventory.secretstore.get_secret("special", "controller", "test_password")
            decrypted_test_pass = test_password.decrypt()
            self.assertEqual(decrypted_test_pass, "p@ssw0rd")

    @pdbexc
    def test_node1_encrypt_decrypt_inmem(self):
        """Test encrypting and decrypting a secret for node1

        Tests the age secret store code.
        """
        secname_inmem = "test_node1_encrypt_decrypt_inmem"
        secvalue_inmem = "red mercury"
        with nnss_test_data as nnss:
            encrypted_str = nnss.inventory.secretstore.encrypt_secret(
                nnss.inventory.hoststore, secname_inmem, secvalue_inmem, ["node1"], [], False, store=False
            )
            secret = AgeSecret(encrypted_str, nnss.progfigsite.nodes.node1.node.sitedata["age_key_path"])
            self.assertEqual(secret.decrypt(), secvalue_inmem)

    @pdbexc
    def test_node1_encrypt_decrypt_ondisk(self):
        """Test encrypting and decrypting a secret for node1 on disk.

        Save a secret to disk, then read it from disk.
        Actually, we save it to disk then comment out the line that saves it,
        because the salt changes every time the secret is encrypted,
        and that generates a new encrypted value every time,
        which is annoying in Git.
        """
        secname_ondisk = "test_node1_encrypt_decrypt_ondisk"
        secvalue_ondisk = "LK-99, a room temperature superconductor, really guys we promise"
        with nnss_test_data as nnss:
            # nnss.inventory.secretstore.encrypt_secret(
            #     nnss.inventory.hoststore, secname_ondisk, secvalue_ondisk, ["node1"], [], False, store=True
            # )
            secret = nnss.inventory.secretstore.get_secret("node", "node1", secname_ondisk)
            self.assertEqual(secret.decrypt(), secvalue_ondisk)


if __name__ == "__main__":
    unittest.main()
