from pathlib import Path
import shutil
import string
import tempfile
import unittest
import venv

import progfiguration
from tests.test_newsite_results import make_venv_newsite

try:
    import tomllib
except ImportError:
    raise RuntimeError("tomllib (from Python 3.11+) is required to run tests")

from progfiguration import cmd, progfigbuild

from tests import pdbexc, skipUnlessAnyEnv, verbose_test_output


class TestRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a temporary directory and create the newsite"""
        cls.tmpdir = Path(tempfile.mkdtemp())
        cls.sitename = "testsite_xyz"
        cls.projectdir = cls.tmpdir / "testproj"
        cls.packagedir = cls.projectdir / "src" / cls.sitename
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
    def test_newsite_builds_runs_zipapp_validates_site(self):
        """Test that it validates from the site 'validate' command

        Slow test, requires a new venv.

        Uses a zipapp for convenience, which also tests that the zipapp functionality works.
        """

        venvdir = self.tmpdir / "venv_test_newsite_validates_site"

        # Create a venv without pip (much faster)
        venv.create(venvdir.as_posix())
        venv_python = venvdir / "bin" / "python"

        # Out of the venv, use progfiguration core to create a site package
        pyzfile = self.tmpdir / "test.pyz"
        progfigbuild.build_progfigsite_zipapp(self.packagedir, self.sitename, pyzfile)

        if verbose_test_output():
            print("Contents of the zipapp:")
            import zipfile

            with zipfile.ZipFile(pyzfile, "r") as z:
                z.printdir()

        # Use the venv python, which is guaranteed not to have progfiguration core or any site installed,
        # to run the newly created zipapp, and validate.
        result = cmd.magicrun(
            [venv_python.as_posix(), pyzfile.as_posix(), "validate"], print_output=verbose_test_output()
        )
        stdout = result.stdout.read()
        self.assertTrue(result.returncode == 0)
        self.assertRegex(stdout, r"Progfigsite \(Python path: '.*'\) is valid.")

    @pdbexc
    @skipUnlessAnyEnv(["PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_SITE"])
    def test_newsite_install_editable(self):
        """Test that it is installable to a venv with 'pip install -e'

        Slow test, requires a new venv.
        """

        venvdir = self.tmpdir / "venv_test_install_editable"

        # Create a venv with pip (slow)
        venv.create(venvdir.as_posix(), with_pip=True)
        venv_python = venvdir / "bin" / "python"

        # Install progfiguration core into the venv.
        # Use its path and install it as editable.
        # This is a hack to avoid having to install over the network (slower, maybe network errors).
        #
        # The parent of the progfiguration core package is the directory containing pyproject.toml
        progfiguration_core_project_path = progfigbuild.find_pyproject_root_from_package_path(progfiguration.__file__)
        cmd.magicrun(
            [
                venv_python.as_posix(),
                "-m",
                "pip",
                "--disable-pip-version-check",
                "install",
                "--editable",
                progfiguration_core_project_path.as_posix(),
            ],
            print_output=verbose_test_output(),
        )

        # Install the site into the venv as editable
        pip_site_result = cmd.magicrun(
            [
                venv_python.as_posix(),
                "-m",
                "pip",
                "--disable-pip-version-check",
                "install",
                "--editable",
                self.projectdir.as_posix(),
            ],
            print_output=verbose_test_output(),
        )
        self.assertTrue(pip_site_result.returncode == 0)

        # Validate the site from within the venv
        venv_site = venvdir / "bin" / self.sitename
        validate_result = cmd.magicrun(
            [
                venv_site.as_posix(),
                "validate",
            ],
            print_output=verbose_test_output(),
        )
        validate_stdout = validate_result.stdout.read()
        self.assertEqual(validate_result.returncode, 0)
        self.assertEqual(validate_stdout, f"Progfigsite (Python path: '{self.sitename}') is valid.\n")

    @pdbexc
    @skipUnlessAnyEnv(["PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_SITE"])
    def test_site_pip_install_editable_development_extras(self):
        """Test that the site is installable as "pip install -e '.[developmenmt]'".

        This is a slow test, as it creates a virtualenv,
        and installs progfiguration core into it.

        Test that the site can be installed as editable
        without progfiguration core installed first.
        Pip installing the '.[development]' extra will install the progfiguration core,
        but first pip will find the version of the site package.
        If finding the version depends on progfiguration core,
        then the test fails.
        Make sure we haven't accidentally required that progfiguration core be installed
        before we can install any site in a venv as editable.
        """

        sitename = "test_spiede"
        venvdir = make_venv_newsite(sitename, self.tmpdir, extras=["development"])

        # Validate the site from within the venv
        venv_site_cmd = venvdir / "bin" / sitename
        validate_result = cmd.magicrun(
            [
                venv_site_cmd.as_posix(),
                "validate",
            ],
            print_output=verbose_test_output(),
        )
        validate_stdout = validate_result.stdout.read()
        self.assertEqual(validate_result.returncode, 0)
        self.assertEqual(validate_stdout, f"Progfigsite (Python path: '{sitename}') is valid.\n")
