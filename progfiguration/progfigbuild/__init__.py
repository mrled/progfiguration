"""Support for building pip and zipapp progfigsite packages"""


from dataclasses import dataclass
from datetime import datetime
import pathlib
import stat
import textwrap
from typing import Callable, List, Optional
import zipfile

import progfiguration
from progfiguration import logger
from progfiguration.cmd import magicrun
from progfiguration.util import import_module_from_filepath


@dataclass
class InjectedFile:
    """A file to inject into the built package"""

    path: pathlib.Path
    """The path to the file relative to the package root."""

    contents: str
    """The contents of the file."""


def generate_builddata_version_py(version: str, build_date: datetime) -> str:
    """Generate the contents of builddata_version.py"""

    builddata_version_py = textwrap.dedent(
        f"""\
        from datetime import datetime
        version = "{version}"
        builddate = datetime.fromisoformat("{build_date.isoformat()}")
        """
    )

    return builddata_version_py


def build_progfigsite_zipapp(
    progfigsite_filesystem_path: pathlib.Path,
    package_out_path: pathlib.Path,
    build_date: Optional[datetime] = None,
    progfiguration_package_path: Optional[pathlib.Path] = None,
    compression: int = zipfile.ZIP_STORED,
):
    """Build a .pyz zipapp progfigsite package

    :param progfigsite_filesystem_path: The path to the progfigsite package, eg "/path/to/progfigsite".
    :param package_out_path: The path where the zipfile will be written.
    :param build_date: The build date to embed in the zipapp.
        If None, the current UTC time will be used.
    :param progfiguration_package_path: The path to the progfiguration package, eg "/path/to/progfiguration".
        If None, the progfiguration package will be copied from the Python path.
        This will only work if progfiguration is installed via pip
        (probably in a venv, possibly editable with 'pip install -e')...
        it won't work if you're running progfiguration itself from a zipapp for some reason.
    :param compression: The compression level to use for the zipapp file.
        This can be zipfile.ZIP_STORED (no compression) or zipfile.ZIP_DEFLATED (deflate compression).
        ZIP_STORED (the default) is faster.

    :return: The path to the zipapp file, eg "/path/to/my_progfigsite.pyz".

    What this function does:

    * Zip up the contents of the site package.
    * Place them inside a subdirectory called 'progfigsite'.
    * Add a __main__.py file to the root of the zip file.
    * Add the progfiguration package to the zip file.
    * Add a shebang to the beginning of the zip file.

    Inspired by the zipapp module code
    <https://github.com/python/cpython/blob/3.11/Lib/zipapp.py>

    We don't use the zipapp code itself because we want more control over what goes into the zipfile,
    like ignoring __pycache__, \*.dist-info, etc.

    We don't need the ProgfigsitePythonPackagePreparer context manager here,
    because we don't need to inject build data into the filesystem before building the zipapp.
    We can inject the build data directly into the zipapp file.
    """

    if progfiguration_package_path is None:
        progfiguration_package_path = pathlib.Path(progfiguration.__file__).parent

    if build_date is None:
        build_date = datetime.utcnow()

    main_py = textwrap.dedent(
        r"""
        from progfiguration.cli import progfiguration_site_cmd
        progfiguration_site_cmd.main("progfigsite")
        """
    )

    def shouldignore(path: pathlib.Path) -> bool:
        """Return True if the path should be excluded from the zipapp file"""
        exacts = [
            "__pycache__",
            ".gitignore",
        ]
        if path.name in exacts:
            return True
        if path.name.endswith(".pyc"):
            return True
        if path.name.endswith(".dist-info"):
            return True
        return False

    progfigsite, progfigsite_modname = import_module_from_filepath(progfigsite_filesystem_path)
    version = progfigsite.mint_version()
    if progfigsite.__file__ is None:
        raise ValueError("Cannot find the filesystem path to the progfigsite package")
    builddata_version_py = generate_builddata_version_py(version, build_date)

    with open(package_out_path, "wb") as fp:
        # Writing a shebang like this is optional in zipapp,
        # but there's no reason not to since it's a valid zip file either way.
        fp.write(b"#!/usr/bin/env python3\n")

        with zipfile.ZipFile(fp, "w", compression=compression) as z:

            # Copy the progfigsite package into the zipfile
            for child in progfigsite_filesystem_path.rglob("*"):
                if shouldignore(child):
                    continue
                child_relname = child.relative_to(progfigsite_filesystem_path)
                # Place the progfigsite package inside a subdirectory called 'progfigsite'.
                # This ignores the actual name of the package,
                # and allows progfiguration to find it when run from the zipfile.
                z.write(child, "progfigsite/" + child_relname.as_posix())

            # Copy the progfiguration package into the zipfile
            for child in progfiguration_package_path.rglob("*"):
                if shouldignore(child):
                    continue
                child_relname = child.relative_to(progfiguration_package_path)
                z.write(child, "progfiguration/" + child_relname.as_posix())

            # Inject build date file
            z.writestr("progfigsite/builddata/version.py", builddata_version_py.encode("utf-8"))

            # Add the __main__.py file to the zipfile root, which is required for zipapps
            z.writestr("__main__.py", main_py.encode("utf-8"))

    # Make the zipapp executable
    package_out_path.chmod(package_out_path.stat().st_mode | stat.S_IEXEC)


def progfigsite_setuptools_builder(
    progfigsite_package_path: pathlib.Path,
    package_out_path: pathlib.Path,
    # config_settings: Optional[Dict[str, Any]] = None,
    # isolation: bool = True,
    # skip_dependency_check: bool = False,
) -> str:
    """Build a progfigsite package with build and setuptools

    Requires that these modules already be installed in the current Python environment.

    Returns the build package path.
    """

    cmd = ["python", "-m", "build", "-s", "-o", package_out_path.as_posix(), progfigsite_package_path.as_posix()]
    result = magicrun(cmd)
    return result.stdout.read()


class ProgfigsitePythonPackagePreparer:
    """A context manager which prepares for building a Python package.

    Preparation consists of finding the project path from the package path
    (see `progfigsite_project_path` and `progfigsite_filesystem_path` properties),
    and injecting build data into the filesystem
    like a version from progfigsite's `mint_version()` and the build date.
    When the context manager exits, the injected files are removed.

    You can use this to build a pip package with build and setuptools like this:

    .. code-block:: python

        with ProgfigsitePythonPackagePreparer("/path/to/progfigsite") as preparer:
            result = subprocess.run(
                ["python", "-m", "build", "-s", "-o", preparer.package_out_path.as_posix(), preparer.progfigsite_project_path.as_posix()],
                check=True,
                capture_output=True,
                cwd=preparer.progfigsite_project_path,
            )
        built_package_path = result.stdout.read()

    See the implementation of `build_progfigsite_pip()` for a more complete example.

    If you want to modify the build in some way,
    or build another kind of package after we prepare the filesystem and inject build data,
    you can do that instead.

    Can be used by progfigsite to do something with the result of `python -m build`,
    like build a package for another package manager.
    """

    def __init__(
        self,
        progfigsite_filesystem_path: pathlib.Path,
        build_date: Optional[datetime] = None,
        progfiguration_package_path: Optional[pathlib.Path] = None,
        injections: Optional[List[InjectedFile]] = None,
        keep_injected_files: bool = False,
    ):
        """

        :param progfigsite_filesystem_path: The path to the progfigsite package, eg "/path/to/progfigsite/src".
        :param build_date: The build date to inject into the package.
            If None, the current date will be used.
        :param progfiguration_package_path: The path to the progfiguration package, eg "/path/to/progfiguration".
            If None, the progfiguration package will be copied from the Python path.
            This will only work if progfiguration is installed to the Python path
            (probably by pip in a venv, and possibly editable with 'pip install -e').
        :param injections: Build data we will inject into the filesystem before building the pip package.
            These injections can go anywhere in the filesystem --
            they aren't limited to the progfigsite package.
            You can inject files into the project directory (containing the pyproject.toml),
            the package directory (containing the actual Python package),
            or maybe even somewhere else entirely.
        :param keep_injected_files: If True, the injected files will be kept after the package is built.
            You will need to remove them manually. Intended for debugging.
        """

        self.progfigsite_filesystem_path = progfigsite_filesystem_path
        """The filesystem path to the progfigsite package, eg `/path/to/progfigsite/src`

        This PACKAGE directory should be the path to the Python package itself with an `__init__.py`.
        It might be inside a subfolder like "src" or "progfigsite" inside the PROJECT directory,
        which is the directory containing a pyproject.toml file.

        See also: `progfigsite_project_path`.
        """

        self.progfiguration_package_path = progfiguration_package_path or pathlib.Path(progfiguration.__file__).parent
        """The filesystem path to the progfiguration package, eg `/path/to/progfiguration`"""

        self.build_date = build_date or datetime.utcnow()
        """The build date to inject into the package version metadata"""

        self.keep_injected_files = keep_injected_files
        """If True, the injected files will be kept after the package is built."""

        progfigsite, progfigsite_modname = import_module_from_filepath(progfigsite_filesystem_path)

        self.minted_version: str = progfigsite.mint_version()
        """The version of the package we are building, generated by a call to the progfigsite's `mint_version()`"""

        builddata_version_py = generate_builddata_version_py(self.minted_version, self.build_date)

        # Find the progfigsite PROJECT path containing a pyproject.toml
        # progfigsite_filesystem_path might be inside a directory called 'src' or 'progfigsite' inside the PROJECT path
        progfigsite_pyproject_toml_path = progfigsite_filesystem_path / "pyproject.toml"
        while not progfigsite_pyproject_toml_path.exists():
            if progfigsite_pyproject_toml_path == progfigsite_pyproject_toml_path.parent:
                raise RuntimeError("Could not find progfigsite project path")
            progfigsite_pyproject_toml_path = progfigsite_pyproject_toml_path.parent

        self.progfigsite_project_path = progfigsite_pyproject_toml_path.parent
        """The filesystem path to the progfigsite project, eg `/path/to/progfigsite`

        This PROJECT directory should be the directory containing a pyproject.toml file.
        It might contain a subfolder like "src" or "progfigsite" containing the Python PACKAGE itself.

        This is the directory you should run `python -m build` from.

        See also: `progfigsite_filesystem_path`.
        """

        self.progfiguration_autovendored_path = progfigsite_filesystem_path / "autovendor" / "progfiguration"
        """The filesystem path to the progfiguration package inside the progfigsite package

        We inject a symlink to the progfiguration package into the progfigsite package
        so that progfiguration can find it when run from the pip package.
        (`python -m build` will dereference the symlink and include the actual progfiguration package in the pip package.)
        """

        self.injections = injections or []
        """Build data we will inject into the filesystem before building the pip package

        We always inject a version.py file containing the version and build date.
        We have to do this on disk before building the pip package;
        we can't inject version metadata into the package after it's built,
        because we need to know the version before we build the package.

        Users may also inject other files if they want to with the `injections` argument.
        """
        self.injections += [
            InjectedFile(
                path=progfigsite_filesystem_path / "builddata" / "version.py",
                contents=builddata_version_py,
            ),
        ]

        self.failed_unlinks: List[str] = []

    def __enter__(self):

        # Inject build data into the packages
        logger.debug(f"Injecting progfiguration symlink {self.progfiguration_autovendored_path}...")
        if self.progfiguration_autovendored_path.exists():
            self.progfiguration_autovendored_path.unlink()
        self.progfiguration_autovendored_path.symlink_to(self.progfiguration_package_path)
        for injection in self.injections:
            with injection.path.open("w") as fp:
                logger.debug(f"Injecting {injection.path}...")
                fp.write(injection.contents)

        # Return self so we can be used as a context manager
        return self

    def __exit__(self, type, value, traceback):

        # Clean up the injected files
        if self.keep_injected_files:
            logger.warning("Keeping injected files for debugging...")
            logger.debug(f"- {self.progfiguration_autovendored_path}")
            for injection in self.injections:
                logger.debug(f"- {injection.path}")
        else:
            try:
                self.progfiguration_autovendored_path.unlink()
                logger.debug(f"Unlinked progfiguration symlink {self.progfiguration_autovendored_path}...")
            except Exception:
                self.failed_unlinks.append(self.progfiguration_autovendored_path)
                logger.debug(f"Failed to unlink progfiguration symlink {self.progfiguration_autovendored_path}...")
            for injection in self.injections:
                try:
                    injection.path.unlink()
                    logger.debug(f"Unlinked {injection.path}...")
                except Exception:
                    self.failed_unlinks.append(injection.path)
                    logger.debug(f"Failed to unlink {injection.path}...")

        # If we were unable to clean up the injected files, notify the user with an error
        if self.failed_unlinks:
            msg = ["Failed to unlink the following files, make sure not to commit them to version control:"]
            for path in self.failed_unlinks:
                msg.append(f"  {path}")
            raise RuntimeError("\n".join(msg))


def build_progfigsite_pip(
    progfigsite_filesystem_path: pathlib.Path,
    package_out_path: pathlib.Path,
    build_date: Optional[datetime] = None,
    progfiguration_package_path: Optional[pathlib.Path] = None,
    keep_injected_files: bool = False,
) -> pathlib.Path:
    """Build a pip package

    :param progfigsite_filesystem_path: The path to the progfigsite package, eg "/path/to/progfigsite".
    :param package_out_path: The path where the zipfile will be written.
    :param build_date: The build date to inject into the package.
        If None, the current date will be used.
    :param progfiguration_package_path: The path to the progfiguration package, eg "/path/to/progfiguration".
        If None, the progfiguration package will be copied from the Python path.
        This will only work if progfiguration is installed via pip
        (probably in a venv, possibly editable with 'pip install -e')...
        it won't work if you're running progfiguration itself from a zipapp for some reason.
    :param keep_injected_files: If True, the injected files will be kept after the package is built.
        You will need to remove them manually.
        Intended for debugging.

    :return: The path to the pip package, eg "/path/to/my_progfigsite/dist/my_progfigsite-0.1.0.tar.gz"
    """

    with ProgfigsitePythonPackagePreparer(
        progfigsite_filesystem_path,
        build_date=build_date,
        progfiguration_package_path=progfiguration_package_path,
        keep_injected_files=keep_injected_files,
    ) as preparer:
        cmd = [
            "python",
            "-m",
            "build",
            "-s",
            "-o",
            package_out_path.as_posix(),
            preparer.progfigsite_package_path.as_posix(),
        ]
        result = magicrun(cmd)
    return pathlib.Path(result.stdout.read())
