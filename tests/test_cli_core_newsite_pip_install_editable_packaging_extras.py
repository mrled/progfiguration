from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
import venv
import zipfile

import progfiguration

from progfiguration import cmd

from tests import pdbexc, skipUnlessAnyEnv, verbose_test_output


def list_tgz(tarball: str) -> list[str]:
    """List the contents of a tarball"""
    with tarfile.open(tarball, "r:gz") as tar:
        return [member.name for member in tar.getmembers()]


def list_whl(whl: str) -> list[str]:
    """List the contents of a wheel (zip file)"""
    with zipfile.ZipFile(whl, "r") as z:
        return [member.filename for member in z.infolist()]


class TestRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up a temporary directory"""
        cls.tmpdir = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary directory"""
        shutil.rmtree(cls.tmpdir.as_posix())

    @pdbexc
    @skipUnlessAnyEnv(["PROGFIGURATION_TEST_SLOW_ALL", "PROGFIGURATION_TEST_SLOW_SITE"])
    def test_site_pip_install_editable_packaging_extras(self):
        """Test that the site can be built and installed with pip.

        This is a slow test, as it creates a fresh virtualenv
        to install the site package into.
        """

        sitename = "test_spiepe"
        venvdir_inst = self.tmpdir / f"venv_inst_{sitename}"
        venvdir_build = self.tmpdir / f"venv_build_{sitename}"

        # Create a venv for building the site
        # Add pip (slow), so we can install the site into it
        venv.create(venvdir_build.as_posix(), with_pip=True)

        # Install progfiguration core into the venv.
        # Use its path and install it as editable.
        # Doing this here means that when setuptools encounters progfiguration
        # as a dependency in the site's pyproject.toml,
        # it will find it in the venv and use that version.
        # This lets us test the site against the local progfiguration core
        # (which may have changes that we need to test),
        # and is also faster than installing over the network.
        #
        # The parent of the progfiguration core package is the directory containing pyproject.toml
        progfiguration_core_project_path = Path(progfiguration.__file__).parent.parent
        cmd.magicrun(
            [
                venvdir_build / "bin" / "pip",
                "--disable-pip-version-check",
                "install",
                "--editable",
                progfiguration_core_project_path,
            ],
            print_output=verbose_test_output(),
        )

        # Make a new site, dedicated to this one test
        projectdir = self.tmpdir / sitename
        packagedir = projectdir / "src" / sitename
        controllerage = self.tmpdir / f"controller.{sitename}.age"
        newsite_result = cmd.magicrun(
            [
                venvdir_build / "bin" / "progfiguration",
                "newsite",
                "--name",
                sitename,
                "--path",
                projectdir,
                "--controller-age-key-path",
                controllerage,
            ],
            print_output=verbose_test_output(),
        )
        self.assertTrue(newsite_result.returncode == 0)

        # Print the contents of pyproject.toml for debugging
        if verbose_test_output():
            pyproject_toml = projectdir / "pyproject.toml"
            print("Contents of pyproject.toml:")
            print(pyproject_toml.read_text())

        # Install the new site into the venv as editable
        #
        # We have to do this because we use a dynamic version in pyproject.toml,
        # and the site has to be importable into the same Python process
        # that runs the build command for this to work,
        # otherwise it will fail with error messages like:
        #   ModuleNotFoundError: test_spibi/version
        #
        # It's also a convenient way to get the site's packaging extras installed.
        site_install_result = cmd.magicrun(
            [
                venvdir_build / "bin" / "pip",
                "--disable-pip-version-check",
                "install",
                "--editable",
                ".[packaging]",
            ],
            cwd=projectdir.as_posix(),
            print_output=verbose_test_output(),
        )

        # Build the site into a pip package
        pip_build = self.tmpdir / "pip_build"
        prog_build_result = cmd.magicrun(
            [
                venvdir_build / "bin" / "progfiguration",
                "build",
                "--progfigsite-fspath",
                packagedir,
                "--progfigsite-modname",
                sitename,
                "pip",
                "--outdir",
                pip_build,
            ],
            cwd=projectdir.as_posix(),
            print_output=verbose_test_output(),
        )
        self.assertTrue(prog_build_result.returncode == 0)

        # Find the pip package in the build directory
        pip_src_pkg = None
        pip_whl_pkg = None
        for child in pip_build.iterdir():
            if verbose_test_output():
                print(f"test_site_pip_install_build_install: Found built pip package: {pip_build} / {child}")
            if child.name.endswith(".tar.gz") and pip_src_pkg is None:
                pip_src_pkg = child
            elif child.name.endswith(".whl") and pip_whl_pkg is None:
                pip_whl_pkg = child
            else:
                raise RuntimeError(f"Unexpected file in pip build directory: {child}")
        if pip_src_pkg is None:
            raise RuntimeError(f"Could not find pip source package in {pip_build}")
        # if pip_whl_pkg is None:
        #     raise RuntimeError(f"Could not find pip binary package in {pip_build}")

        pkgvers = str(pip_src_pkg).replace(".tar.gz", "").split("-")[-1]
        pip_src_files = list_tgz(pip_src_pkg)
        # pip_whl_files = list_whl(pip_whl_pkg)

        if verbose_test_output():
            msg = "Built pip packages:"
            msg += f"\n  List of files in build output directory at {pip_build}:"
            msg += "\n  - " + "\n  - ".join([child.name for child in pip_build.iterdir()])
            msg += f"\n  Full list of contents for source package at {pip_src_pkg}:"
            msg += "\n  - " + "\n  - ".join(pip_src_files)
            # msg += f"\n  Full list of contents for binary package at {pip_whl_pkg}:"
            # msg += "\n  - " + "\n  - ".join(pip_whl_files)
            msg += f"\n  Detected version as {pkgvers}"
            msg += "\n"
            print(msg)

        # Examine the pip packages
        # Make sure it includes what we expect,
        # especially non-Python files like inventory.conf which are not included by default.
        # Note that the wheel won't include things pyproject.toml,
        # and that the source package will place all files in a subdirectory
        # named after the package and version.
        required_files = [
            f"__init__.py",
            f"inventory.conf",
            f"builddata/static_include/progfiguration/__init__.py",
        ]
        missing_files = []
        for reqfile in required_files:
            # The pip src package has all filenames prefixed with the package name and version,
            # but the wheel does not.
            # if f"{sitename}-{pkgvers}/{reqfile}" not in pip_src_files or reqfile not in pip_whl_files:
            #     missing_files.append(reqfile)
            if f"{sitename}-{pkgvers}/src/{sitename}/{reqfile}" not in pip_src_files:
                missing_files.append(reqfile)
        if missing_files:
            setuptools_version = cmd.magicrun(
                [venvdir_build / "bin" / "python", "-c", "import setuptools; print(setuptools.__version__)"]
            ).stdout.read()
            msg += f"\nSetuptools inside the venv is version {setuptools_version}"
            raise RuntimeError(f"Spot checking for required files, but at least some are missing: {missing_files}")

        # Make sure the version is not the fallback version,
        # which would indicate that the version was not injected into the builddata.
        self.assertTrue(pkgvers != "0.0.1a0")

        # Create a venv to install the package to
        # Add pip (slow), so we can install the site into it
        venv.create(venvdir_inst.as_posix(), with_pip=True)

        # Install the site into the venv as editable
        pip_site_result = cmd.magicrun(
            [
                venvdir_inst / "bin" / "python",
                "-m",
                "pip",
                "--disable-pip-version-check",
                "install",
                pip_src_pkg,
            ],
            print_output=verbose_test_output(),
        )
        self.assertTrue(pip_site_result.returncode == 0)

        # Validate the site from within the venv
        validate_result = cmd.magicrun(
            [venvdir_inst / "bin" / sitename, "validate"],
            print_output=verbose_test_output(),
        )
        validate_stdout = validate_result.stdout.read()
        self.assertEqual(validate_result.returncode, 0)
        self.assertEqual(validate_stdout, f"Progfigsite (Python path: '{sitename}') is valid.\n")
