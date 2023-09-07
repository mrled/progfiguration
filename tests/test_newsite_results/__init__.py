from pathlib import Path
from typing import Optional
import venv

import progfiguration
from progfiguration import cmd
from progfiguration.progfigbuild import find_pyproject_root_from_package_path

from tests import verbose_test_output


def make_venv_newsite(sitename: str, tmpdir: Path, extras: Optional[list[str]] = None) -> Path:
    """Create a new site in a temporary directory, and return the path to it

    This requires some set up, so we extract it into a function.

    It's particularly important to make sure that we install progfiguration core
    from the local source tree, not from PyPI.
    """

    if extras is None:
        extras = []

    venvdir = tmpdir / f"venv_build_{sitename}"

    # Create a venv for building the site
    # Add pip (slow), so we can install the site into it
    venv.create(venvdir.as_posix(), with_pip=True)

    # Install progfiguration core into the venv.
    # Use its path and install it as editable.
    # Doing this here means that when setuptools encounters progfiguration
    # as a dependency in the site's pyproject.toml,
    # it will find it in the venv and use that version.
    # This lets us test the site against the local progfiguration core
    # (which may have changes that we need to test),
    # and is also faster than installing over the network.
    progfiguration_core_project_path = find_pyproject_root_from_package_path(progfiguration.__file__)
    cmd.magicrun(
        [
            venvdir / "bin" / "pip",
            "--disable-pip-version-check",
            "install",
            "--editable",
            progfiguration_core_project_path,
        ],
        print_output=verbose_test_output(),
    )

    # Make a new site, dedicated to this one test
    projectdir = tmpdir / sitename
    packagedir = projectdir / "src" / sitename
    controllerage = tmpdir / f"controller.{sitename}.age"
    newsite_result = cmd.magicrun(
        [
            venvdir / "bin" / "progfiguration",
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

    # Print the contents of pyproject.toml for debugging
    if verbose_test_output():
        pyproject_toml = projectdir / "pyproject.toml"
        print("Contents of pyproject.toml:")
        print(pyproject_toml.read_text())

    # The sitepath is the path to the site, with extras in brackets.
    # We always cd into the project path, so the path is just "."
    # and we can add extras in brackets.
    # This value might become just "."
    # or it might become ".[development]" for a single extra
    # or even ".[development,testing]" for multiple extras.
    # <https://stackoverflow.com/questions/66152178/pip-install-multiple-extra-dependencies-of-a-single-package-via-requirement-file>
    sitepath = "."
    if extras:
        sitepath += f"[{','.join(extras)}]"

    # Install the site into the venv as editable
    pip_site_result = cmd.magicrun(
        [
            venvdir / "bin" / "pip",
            "--disable-pip-version-check",
            "install",
            "--editable",
            sitepath,
        ],
        cwd=projectdir.as_posix(),
        print_output=verbose_test_output(),
    )

    return venvdir
