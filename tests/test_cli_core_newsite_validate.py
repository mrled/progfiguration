from pathlib import Path
import shutil
import tempfile
import unittest
import venv

try:
    import tomllib
except ImportError:
    raise RuntimeError("tomllib (from Python 3.11+) is required to run tests")

from progfiguration import cmd, progfigbuild

from tests import pdbexc, skipUnlessAnyEnv


class TestRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a temporary directory and create the newsite"""
        cls.tmpdir = Path(tempfile.mkdtemp())
        cls.sitename = "testsite_xyz"
        cls.projectdir = cls.tmpdir / "testproj"
        cls.packagedir = cls.projectdir / cls.sitename
        cls.controllerage = cls.tmpdir / "controller.age"
        cls.pyproject = cls.projectdir / "pyproject.toml"

        # Create the new site in the temp directory
        cls.newsite_result = cmd.magicrun(
            [
                "progfiguration",
                "newsite",
                "--name",
                cls.sitename,
                "--path",
                cls.projectdir.as_posix(),
                "--controller-age-key-path",
                cls.controllerage.as_posix(),
            ],
            print_output=False,
        )

        # cmd.magicrun(["find", cls.tmpdir])

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary directory"""
        shutil.rmtree(cls.tmpdir.as_posix())

    @pdbexc
    def test_newsite_successful(self):
        """Test that the newsite subcommand succeeded"""
        self.assertEqual(self.newsite_result.returncode, 0)
        newsite_stdout = self.newsite_result.stdout.read()
        self.assertIn(f"Created new progfigsite package '{self.sitename}' at", newsite_stdout)

    @pdbexc
    def test_newsite_files_created(self):
        """Test the newsite subcommand"""

        pyproj = tomllib.load(self.pyproject.open("rb"))
        self.assertEqual(pyproj["project"]["name"], self.sitename)
        self.assertEqual(pyproj["project"]["scripts"][self.sitename], f"{self.sitename}.cli.progfigsite_shim:main")

    @pdbexc
    def test_newsite_validates_core(self):
        """Test that it validates from the core 'validate' command"""

        # Run validate against the new site
        result = cmd.magicrun(
            [
                "progfiguration",
                "validate",
                "--progfigsite-fspath",
                self.packagedir.as_posix(),
                "--progfigsite-modname",
                self.sitename,
            ],
            print_output=False,
        )
        stdout = result.stdout.read()
        self.assertTrue(result.returncode == 0)
        self.assertRegex(stdout, r"Progfigsite \(Python path: '.*'\) is valid.")

    @pdbexc
    @skipUnlessAnyEnv(["PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_SITE"])
    def test_newsite_validates_site(self):
        """Test that it validates from the site 'validate' command

        Slow test, requires a new venv.
        """

        venvdir = self.tmpdir / "venv"

        # Create a venv without pip (much faster)
        venv.create(venvdir.as_posix())
        venv_python = venvdir / "bin" / "python"

        # Out of the venv, use progfiguration core to create a site package
        pyzfile = self.tmpdir / "test.pyz"
        progfigbuild.build_progfigsite_zipapp(self.packagedir, self.sitename, pyzfile)

        # Show all the files in the zipapp
        # import zipfile
        # with zipfile.ZipFile(pyzfile, "r") as z:
        #     z.printdir()

        # Use the venv python, which is guaranteed not to have progfiguration core or any site installed,
        # to run the newly created zipapp, and validate.
        result = cmd.magicrun([venv_python.as_posix(), pyzfile.as_posix(), "validate"], print_output=False)
        stdout = result.stdout.read()
        self.assertTrue(result.returncode == 0)
        self.assertRegex(stdout, r"Progfigsite \(Python path: '.*'\) is valid.")
