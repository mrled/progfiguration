import io
import os
import sys
import tempfile
import unittest

from tests import pdbexc

try:
    import tomllib
except ImportError:
    raise RuntimeError("tomllib (from Python 3.11+) is required to run tests")

from progfiguration import cmd


class TestRun(unittest.TestCase):
    @pdbexc
    def test_newsite_basic(self):
        """Test the newsite subcommand"""

        sitename = "testsite_xyz"
        with tempfile.TemporaryDirectory() as tmpdir:
            projectdir = os.path.join(tmpdir, "testproj")
            packagedir = os.path.join(projectdir, sitename)
            controllerage = os.path.join(tmpdir, "controller.age")

            # Create the new site in the temp directory
            newsite_result = cmd.magicrun(
                [
                    "progfiguration",
                    "newsite",
                    "--name",
                    sitename,
                    "--path",
                    projectdir,
                    "--controller-age-key-path",
                    controllerage,
                ],
                print_output=False,
            )
            newsite_stdout = newsite_result.stdout.read()
            self.assertIn(f"Created new progfigsite package '{sitename}' at", newsite_stdout)

            pyproj = tomllib.load(open(os.path.join(projectdir, "pyproject.toml"), "rb"))
            self.assertEqual(pyproj["project"]["name"], sitename)
            self.assertEqual(pyproj["project"]["scripts"]["progfigsite"], f"{sitename}.cli.progfigsite_shim:main")

            # Run validate against the new site
            validate_result = cmd.magicrun(
                ["progfiguration", "validate", "--progfigsite-filesystem-path", packagedir],
                print_output=False,
            )
            validate_stdout = validate_result.stdout.read()
            self.assertRegex(validate_stdout, r"Progfigsite \(Python path: '.*'\) is valid.")
