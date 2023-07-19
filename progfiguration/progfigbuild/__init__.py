"""Support for building pip and zipapp progfigsite packages"""


from datetime import datetime
import pathlib
import stat
import textwrap
from typing import Optional
import zipfile

import progfiguration


def build_progfigsite_zipapp(
    package_out_path: pathlib.Path,
    progfigsite_package_path: pathlib.Path,
    progfiguration_package_path: Optional[pathlib.Path] = None,
    compression: int = zipfile.ZIP_STORED,
) -> pathlib.Path:
    """Build a .pyz zipapp progfigsite package

    Args:
        package_out_path: The path where the zipfile will be written.
        progfigsite_package_path: The path to the site package, eg "/path/to/my_progfigsite"
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

    TODO: how should build_progfigsite_zipapp handle versions?
    Should we allow overriding progfiguration and progfigsite versions by overwriting files in the zipapp?

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

    main_py = textwrap.dedent(
        r"""
        from progfiguration.cli import progfiguration_cmd
        progfiguration_cmd.main()
        """
    )

    builddata_builddate_py = textwrap.dedent(
        f"""\
        from datetime import datetime
        builddate_str = "{datetime.utcnow().isoformat()}"
        builddate = datetime.fromisoformat(builddate_str)
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

    with open(package_out_path, "wb") as fp:
        # Writing a shebang like this is optional in zipapp,
        # but there's no reason not to since it's a valid zip file either way.
        fp.write(b"#!/usr/bin/env python3\n")

        with zipfile.ZipFile(fp, "w", compression=compression) as z:

            # Copy the progfigsite package into the zipfile
            for child in progfigsite_package_path.rglob("*"):
                if shouldignore(child):
                    continue
                child_relname = child.relative_to(progfigsite_package_path)
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
            z.writestr("progfiguration/builddata/builddate.py", builddata_builddate_py.encode("utf-8"))

            # Add the __main__.py file to the zipfile root, which is required for zipapps
            z.writestr("__main__.py", main_py.encode("utf-8"))

    # Make the zipapp executable
    package_out_path.chmod(package_out_path.stat().st_mode | stat.S_IEXEC)
