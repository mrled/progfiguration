"""The command line interface for progfiguration"""

import argparse
import importlib
import importlib.metadata
import pathlib
import sys

import progfiguration
from progfiguration import progfigbuild
from progfiguration.cli.util import (
    configure_logging,
    get_command_help,
    idb_excepthook,
    progfiguration_error_handler,
    progfiguration_log_levels,
)
from progfiguration.progfigsite_validator import validate
from progfiguration.util import import_module_from_filepath


def _find_progfigsite_module(parser: argparse.ArgumentParser, parsed: argparse.Namespace):
    """Find the progfigsite module from the command line arguments"""

    if parsed.progfigsite_filesystem_path:
        progfigsite_filesystem_path = parsed.progfigsite_filesystem_path
        progfigsite, progfigsite_module_path = import_module_from_filepath(parsed.progfigsite_filesystem_path)
    elif parsed.progfigsite_python_path:
        progfigsite_module_path = parsed.progfigsite_python_path
        progfigsite = importlib.import_module(progfigsite_module_path)
        progfigsite_filesystem_path = pathlib.Path(progfigsite.__file__).parent
    else:
        parser.error(f"Missing progfigsite path option")

    return (progfigsite, progfigsite_module_path, progfigsite_filesystem_path)


def _action_version_core(quiet: bool = False):
    """Retrieve the version of progfiguration core"""

    coreversion = importlib.metadata.version("progfiguration")
    if quiet:
        print(coreversion)
    else:
        result = [
            f"progfiguration core:",
            f"    path: {pathlib.Path(progfiguration.__file__).parent}",
            f"    version: {coreversion}",
        ]
        print("\n".join(result))


def _action_validate(module_path: str):
    """Validate a progfigsite module

    Arguments:
        module_path -- The Python path to the progfigsite module
    """
    validation = validate(module_path)
    if validation.is_valid:
        print(f"Progfigsite (Python path: '{module_path}') is valid.")
    else:
        print(f"Progfigsite (Python path: '{module_path}') has {len(validation.errors)} errors:")
    for attrib in validation.errors:
        print(attrib.errstr)


def _make_parser():
    parser = argparse.ArgumentParser("progfiguration core management tool")

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Open the debugger if an unhandled exception is encountered",
    )

    parser.add_argument(
        "--log-stderr",
        default="NOTSET",
        choices=progfiguration_log_levels,
        help="Log level to send to stderr. Defaults to NOTSET (all messages, including debug). NONE to disable.",
    )

    # options for finding the progfigsite
    site_opts = argparse.ArgumentParser(add_help=False)
    site_grp = site_opts.add_mutually_exclusive_group(required=True)
    site_grp.add_argument(
        "--progfigsite-filesystem-path",
        type=pathlib.Path,
        help="The filesystem path to a progfigsite package, like /path/to/progfigsite. If neither this nor --progfigsite-python-path is passed, look for a 'progfigsite' package in the Python path.",
    )
    site_grp.add_argument(
        "--progfigsite-python-path",
        type=str,
        help="The python path to a progfigsite package, like 'my_progfigsite' or 'one.two.three.progfigsite'. If neither this nor --progfigsite-filesystem-path is passed, look for a 'progfigsite' package in the Python path.",
    )

    subparsers = parser.add_subparsers(dest="action", required=True)

    # version-core subcommand
    svn = subparsers.add_parser("version", description="Show progfiguration core version")
    svn.add_argument("--quiet", "-q", action="store_true", help="Only print the version string")

    # build subcommand
    sub_build = subparsers.add_parser("build", parents=[site_opts], description="Build the package")
    sub_build_subparsers = sub_build.add_subparsers(dest="buildaction", required=True)
    sub_build_sub_pyz = sub_build_subparsers.add_parser(
        "pyz",
        description="Build a zipapp .pyz file containing the Python module. Must be run from an editable install.",
    )
    sub_build_sub_pyz.add_argument("pyzfile", type=pathlib.Path, help="Save the resulting pyz file to this path")
    sub_build_sub_pip = sub_build_subparsers.add_parser(
        "pip",
        description="Build a pip package containing the Python module. Must be run from an editable install.",
    )
    sub_build_sub_pip.add_argument(
        "--outdir",
        default="./dist",
        type=pathlib.Path,
        help="Save the resulting pip package to this path. Defaults to ./dist",
    )
    sub_build_sub_pip.add_argument(
        "--keep-injected-files",
        action="store_true",
        default=False,
        help="Keep the injected files in the package after building. This is useful for debugging.",
    )

    # validate subcommand
    sub_validate = subparsers.add_parser(
        "validate", parents=[site_opts], description="Validate the progfigsite that it matches the required API"
    )

    # Return
    return parser


def _main_implementation(*arguments):
    parser = _make_parser()
    parsed = parser.parse_args(arguments[1:])

    if parsed.debug:
        sys.excepthook = idb_excepthook
    configure_logging(parsed.log_stderr)

    if parsed.action == "version":
        _action_version_core(quiet=parsed.quiet)
    elif parsed.action == "build":
        progfigsite, progfigsite_modpath, progfigsite_fspath = _find_progfigsite_module(parser, parsed)
        # TODO: how will sites extend this?
        if parsed.buildaction == "pyz":
            progfigbuild.build_progfigsite_zipapp(progfigsite_fspath, parsed.pyzfile)
        elif parsed.buildaction == "pip":
            progfigbuild.build_progfigsite_pip(
                progfigsite_fspath, parsed.outdir, keep_injected_files=parsed.keep_injected_files
            )
        else:
            parser.error(f"Unknown buildaction {parsed.buildaction}")
    elif parsed.action == "validate":
        progfigsite, progfigsite_modpath, progfigsite_fspath = _find_progfigsite_module(parser, parsed)
        _action_validate(progfigsite_modpath)
    else:
        parser.error(f"Unknown action {parsed.action}")


def main():
    """The main entry point for the progfiguration command-line interface"""
    progfiguration_error_handler(_main_implementation, *sys.argv)


__doc__ = f"""
The command-line interface to progfiguration core.

This command is installed with the progfiguration package.
When packaging a progfigsite in a pyz, it is not available.

This command can perform general progfiguration related tasks that don't need a site,
as well as tasks that validate or build site packages.

## Command line help

The program's command-line help is reproduced here:

```text
{get_command_help("progfiguration", _make_parser())}
```
"""
