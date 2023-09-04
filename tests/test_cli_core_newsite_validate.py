from pathlib import Path
import shutil
import string
import tempfile
import textwrap
import unittest
import venv

import progfiguration

try:
    import tomllib
except ImportError:
    raise RuntimeError("tomllib (from Python 3.11+) is required to run tests")

from progfiguration import cmd, progfigbuild

from tests import pdbexc, skipUnlessAnyEnv, verbose_test_output


_pyproject_toml_template = string.Template(
    """\
[project]
name = "$sitename"
dynamic = ["version"]
description = "Test project"
[project.scripts]
$sitename = "$sitename.cli.progfigsite_shim:main"
[project.optional-dependencies]
development = ["progfiguration @ file://$progfiguration_proj_path"]
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[tool.setuptools.package-data]
example_site = ["*"]
[tool.setuptools.dynamic.version]
attr = "$sitename.version.get_version"
[tool.black]
line-length = 120
"""
)
"""Template for pyproject.toml files created by tests

* Use the sitename as the package and script names.
* Use the local filesystem path to progfiguration core.
  This is much faster and more reliable for tests than installing from PyPI,
  and allows us to test local changes to progfiguration core.
"""


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
        progfiguration_core_project_path = Path(progfiguration.__file__).parent.parent
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
        venvdir = self.tmpdir / f"venv_{sitename}"

        # Make a new site, dedicated to this one test
        projectdir = self.tmpdir / sitename
        packagedir = projectdir / sitename
        controllerage = self.tmpdir / f"controller.{sitename}.age"
        newsite_result = cmd.magicrun(
            [
                "progfiguration",
                "newsite",
                "--name",
                sitename,
                "--path",
                projectdir.as_posix(),
                "--controller-age-key-path",
                controllerage.as_posix(),
            ],
            print_output=verbose_test_output(),
        )
        self.assertTrue(newsite_result.returncode == 0)

        # Modify pyproject.toml to install progfiguration core from the local filesystem.
        progfiguration_proj_path = Path(progfiguration.__file__).parent.parent
        pyproject_toml = projectdir / "pyproject.toml"
        with pyproject_toml.open("w") as fp:
            fp.write(
                _pyproject_toml_template.substitute(
                    sitename=sitename,
                    progfiguration_proj_path=progfiguration_proj_path,
                )
            )
        if verbose_test_output():
            print("Contents of pyproject.toml:")
            print(pyproject_toml.read_text())

        # Create a venv
        # Add pip (slow), so we can install the site and its core dependency into the venv
        venv.create(venvdir.as_posix(), with_pip=True)
        venv_python = venvdir / "bin" / "python"

        # Install the site into the venv as editable
        pip_site_result = cmd.magicrun(
            [
                venv_python.as_posix(),
                "-m",
                "pip",
                "--disable-pip-version-check",
                "install",
                "--editable",
                ".[development]",
            ],
            cwd=projectdir.as_posix(),
            print_output=verbose_test_output(),
        )
        self.assertTrue(pip_site_result.returncode == 0)

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

    @pdbexc
    # @skipUnlessAnyEnv(["PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_SITE"])
    @unittest.skip("Broken until we implement src layout")
    def test_site_pip_install_build_install(self):
        """Test that the site can be built and installed with pip.

        This is a slow test, as it creates a fresh virtualenv
        to install the site package into.
        """

        sitename = "test_spibi"
        venvdir = self.tmpdir / f"venv_{sitename}"

        # Make a new site, dedicated to this one test
        projectdir = self.tmpdir / sitename
        packagedir = projectdir / sitename
        controllerage = self.tmpdir / f"controller.{sitename}.age"
        newsite_result = cmd.magicrun(
            [
                "progfiguration",
                "newsite",
                "--name",
                sitename,
                "--path",
                projectdir.as_posix(),
                "--controller-age-key-path",
                controllerage.as_posix(),
            ],
            print_output=verbose_test_output(),
        )
        self.assertTrue(newsite_result.returncode == 0)

        # Modify pyproject.toml to install progfiguration core from the local filesystem.
        progfiguration_proj_path = Path(progfiguration.__file__).parent.parent
        pyproject_toml = projectdir / "pyproject.toml"
        with pyproject_toml.open("w") as fp:
            fp.write(
                _pyproject_toml_template.substitute(
                    sitename=sitename,
                    progfiguration_proj_path=progfiguration_proj_path,
                )
            )

        # Build the site into a pip package
        pip_build = self.tmpdir / "pip_build"
        prog_build_result = cmd.magicrun(
            [
                "progfiguration",
                "build",
                "--progfigsite-fspath",
                packagedir.as_posix(),
                "--progfigsite-modname",
                sitename,
                "pip",
                "--outdir",
                pip_build.as_posix(),
            ],
            print_output=verbose_test_output(),
        )
        self.assertTrue(prog_build_result.returncode == 0)

        # Find the pip package in the build directory
        pip_package = None
        for child in pip_build.iterdir():
            if verbose_test_output():
                print(f"{pip_build} / {child}")
            if child.name.endswith(".tar.gz"):
                pip_package = child
                break
        if pip_package is None:
            raise RuntimeError(f"Could not find pip package in {pip_build}")

        # Create a venv
        # Add pip (slow), so we can install the site into it
        venv.create(venvdir.as_posix(), with_pip=True)
        venv_python = venvdir / "bin" / "python"

        # Install the site into the venv as editable
        pip_site_result = cmd.magicrun(
            [
                venv_python.as_posix(),
                "-m",
                "pip",
                "--disable-pip-version-check",
                "install",
                pip_package.as_posix(),
            ],
            print_output=verbose_test_output(),
        )
        self.assertTrue(pip_site_result.returncode == 0)

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
