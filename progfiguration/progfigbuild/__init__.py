"""Support for building pip and zipapp progfigsite packages"""


from dataclasses import dataclass
from datetime import datetime
import pathlib
import stat
import textwrap
from typing import Any, Callable, Dict, Optional
import zipfile

import progfiguration
from progfiguration import logger, sitewrapper
from progfiguration.cmd import run


@dataclass
class InjectedFile:
    """A file to inject into the zipapp

    Properties:
        path: The path to the file relative to the subpackage.
        contents: The contents of the file.
    """

    path: pathlib.Path
    contents: str


def generate_builddata_version_py(build_date: datetime) -> str:
    """Generate the contents of builddata_version.py"""

    progfigsite_minted_version = sitewrapper.progfigsite.mint_version()
    builddata_version_py = textwrap.dedent(
        f"""\
        from datetime import datetime
        version = "{progfigsite_minted_version}"
        builddate = datetime.fromisoformat("{build_date.isoformat()}")
        """
    )

    return builddata_version_py


def build_progfigsite_zipapp(
    package_out_path: pathlib.Path,
    build_date: Optional[datetime] = None,
    progfiguration_package_path: Optional[pathlib.Path] = None,
    compression: int = zipfile.ZIP_STORED,
) -> pathlib.Path:
    """Build a .pyz zipapp progfigsite package

    Args:
        package_out_path: The path where the zipfile will be written.
        build_date: The build date to embed in the zipapp.
            If None, the current UTC time will be used.
        progfiguration_package_path: The path to the progfiguration package, eg "/path/to/progfiguration"
            If None, the progfiguration package will be copied from the Python path.
            This will only work if progfiguration is installed via pip
            (probably in a venv, possibly editable with 'pip install -e')...
            it won't work if you're running progfiguration itself from a zipapp for some reason.
        compression: The compression level to use for the zipapp file.
            This can be zipfile.ZIP_STORED (no compression) or zipfile.ZIP_DEFLATED (deflate compression).
            ZIP_STORED (the default) is faster.

    Returns:
        The path to the zipapp file, eg "/path/to/my_progfigsite.pyz"

    What this function does:

    * Zip up the contents of the site package.
    * Place them inside a subdirectory called 'progfigsite'.
    * Add a __main__.py file to the root of the zip file.
    * Add the progfiguration package to the zip file.
    * Add a shebang to the beginning of the zip file.

    Inspired by the zipapp module code
    <https://github.com/python/cpython/blob/3.11/Lib/zipapp.py>

    We don't use the zipapp code itself because we want more control over what goes into the zipfile,
    like ignoring __pycache__, *.dist-info, etc.
    """

    if progfiguration_package_path is None:
        progfiguration_package_path = pathlib.Path(progfiguration.__file__).parent

    if build_date is None:
        build_date = datetime.utcnow()

    main_py = textwrap.dedent(
        r"""
        from progfiguration.cli import progfiguration_cmd
        progfiguration_cmd.main()
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

    progfigsite_fs_path = sitewrapper.get_progfigsite_path()

    with open(package_out_path, "wb") as fp:
        # Writing a shebang like this is optional in zipapp,
        # but there's no reason not to since it's a valid zip file either way.
        fp.write(b"#!/usr/bin/env python3\n")

        with zipfile.ZipFile(fp, "w", compression=compression) as z:

            # Copy the progfigsite package into the zipfile
            for child in progfigsite_fs_path.rglob("*"):
                if shouldignore(child):
                    continue
                child_relname = child.relative_to(progfigsite_fs_path)
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
            z.writestr("progfigsite/builddata/version.py", generate_builddata_version_py(build_date).encode("utf-8"))

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

    result = run(cmd)

    # from build import ProjectBuilder
    # from build.env import DefaultIsolatedEnv
    # import build

    # if config_settings is None:
    #     config_settings = {}

    # with DefaultIsolatedEnv() as env:
    #     builder = ProjectBuilder.from_isolated_env(env, progfigsite_package_path.as_posix())
    #     # first install the build dependencies
    #     env.install(builder.build_system_requires)
    #     # then get the extra required dependencies from the backend (which was installed in the call above :P)
    #     env.install(builder.get_requires_for_build(progfigsite_package_path.as_posix()))
    #     return builder.build(progfigsite_package_path.as_posix(), package_out_path.as_posix(), config_settings)

    # # result = build.build_package(
    # #     progfigsite_package_path.as_posix(),
    # #     package_out_path.as_posix(),
    # #     ["sdist"],
    # #     config_settings,
    # #     isolation,
    # #     skip_dependency_check,
    # # )

    # runpy.run_path(
    #     "build",
    # )

    return result.stdout


def build_progfigsite_pip(
    package_out_path: pathlib.Path,
    build_date: Optional[datetime] = None,
    progfiguration_package_path: Optional[pathlib.Path] = None,
    builder_function: Callable = progfigsite_setuptools_builder,
    keep_injected_files: bool = False,
) -> pathlib.Path:
    """Build a pip package

    Args:
        package_out_path: The path where the zipfile will be written.
        build_date: The build date to inject into the package.
            If None, the current date will be used.
        progfiguration_package_path: The path to the progfiguration package, eg "/path/to/progfiguration"
            If None, the progfiguration package will be copied from the Python path.
            This will only work if progfiguration is installed via pip
            (probably in a venv, possibly editable with 'pip install -e')...
            it won't work if you're running progfiguration itself from a zipapp for some reason.
        builder_function: A function which builds the pip package.
            See the `progfigsite_setuptools_builder()` function for what arguments it should take.
            TODO: Improve builder_function documentation.
            You can supply your own builder function if you prefer to build pip packages via some other method.
        keep_injected_files: If True, the injected files will be kept after the package is built.
            You will need to remove them manually.
            Intended for debugging.

    Returns:
        The path to the pip package, eg "/path/to/my_progfigsite/dist/my_progfigsite-0.1.0.tar.gz"
    """

    if progfiguration_package_path is None:
        progfiguration_package_path = pathlib.Path(progfiguration.__file__).parent

    if build_date is None:
        build_date = datetime.utcnow()

    package_out_path.mkdir(parents=True, exist_ok=True)

    # This is the progfigsite PACKAGE path containing an __init__.py
    # This might be inside a directory called 'src' or 'progfigsite' inside the PROJECT path (below)
    progfigsite_package_path = sitewrapper.get_progfigsite_path()

    # Find the progfigsite PROJECT path containing a pyproject.toml
    progfigsite_pyproject_toml_path = progfigsite_package_path / "pyproject.toml"
    while not progfigsite_pyproject_toml_path.exists():
        if progfigsite_pyproject_toml_path == progfigsite_pyproject_toml_path.parent:
            raise RuntimeError("Could not find progfigsite project path")
        progfigsite_pyproject_toml_path = progfigsite_pyproject_toml_path.parent
    progfigsite_project_path = progfigsite_pyproject_toml_path.parent

    progfiguration_autovendored_path = progfigsite_package_path / "autovendor" / "progfiguration"

    # Inject build data into the packages.
    # We have to do this on disk before building the pip package.
    injections = [
        InjectedFile(
            path=progfigsite_package_path / "builddata" / "version.py",
            contents=generate_builddata_version_py(build_date),
        ),
    ]

    # We wrap our call to build the pip package in a try/finally block
    # which ensures we don't leave any of our injected files on disk whether the build succeeds or fails.
    failed_unlinks = []
    try:
        # Inject build data into the packages
        logger.debug(f"Injecting progfiguration symlink {progfiguration_autovendored_path}...")
        if progfiguration_autovendored_path.exists():
            progfiguration_autovendored_path.unlink()
        progfiguration_autovendored_path.symlink_to(progfiguration_package_path)
        for injection in injections:
            with injection.path.open("w") as fp:
                logger.debug(f"Injecting {injection.path}...")
                fp.write(injection.contents)

        # Build the pip package
        built = builder_function(progfigsite_project_path, package_out_path)

    finally:
        # Clean up the injected files
        if keep_injected_files:
            logger.warning("Keeping injected files for debugging...")
            logger.debug(f"- {progfiguration_autovendored_path}")
            for injection in injections:
                logger.debug(f"- {injection.path}")
        else:
            try:
                progfiguration_autovendored_path.unlink()
                logger.debug(f"Unlinked progfiguration symlink {progfiguration_autovendored_path}...")
            except Exception:
                failed_unlinks.append(progfiguration_autovendored_path)
                logger.debug(f"Failed to unlink progfiguration symlink {progfiguration_autovendored_path}...")
            for injection in injections:
                try:
                    injection.path.unlink()
                    logger.debug(f"Unlinked {injection.path}...")
                except Exception:
                    failed_unlinks.append(injection.path)
                    logger.debug(f"Failed to unlink {injection.path}...")

    # If we were unable to clean up the injected files, notify the user with an error
    if failed_unlinks:
        msg = ["Failed to unlink the following files, make sure not to commit them to version control:"]
        for path in failed_unlinks:
            msg.append(f"  {path}")
        raise RuntimeError("\n".join(msg))

    return built
